import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from accounts.decorators import management_or_superuser_required
from todo.models import Task

from .models import KPITask

# CRITICAL WINDOWS PATCH: Catching OSError so WeasyPrint doesn't crash the server
try:
    from weasyprint import CSS, HTML
except (ImportError, OSError):
    HTML = None

User = get_user_model()


@login_required
@management_or_superuser_required
def management_dashboard(request):
    """
    Management Dashboard showing KPIs for Staff members.
    """
    staff_users = User.objects.filter(role="Staff")
    selected_staff_id = request.GET.get("staff_id")

    if selected_staff_id:
        selected_staff = User.objects.filter(id=selected_staff_id, role="Staff").first()
    else:
        selected_staff = staff_users.first()

    # Generate past 14 days of data
    today = timezone.now().date()
    labels = []
    data_points = []
    is_weekend = []

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        weekday = date.weekday()

        labels.append(date.strftime("%a, %b %d"))
        is_wknd = weekday >= 5
        is_weekend.append(is_wknd)

        # Query actual KPITask data, filtering out 'Pending' statuses
        if selected_staff:
            daily_tasks = KPITask.objects.filter(
                staff_member=selected_staff, created_at__date=date, status__in=["Yes", "No"]
            )

            if daily_tasks.exists():
                # Yes = 100, No = 0
                total_score = sum(100 for t in daily_tasks if t.status == "Yes")
                avg_grade = total_score / daily_tasks.count()
                data_points.append(round(avg_grade, 1))
            else:
                data_points.append(0)
        else:
            data_points.append(0)

    # Get all KPI tasks for the selected staff to display in the table
    staff_kpi_tasks = None
    if selected_staff:
        staff_kpi_tasks = KPITask.objects.filter(staff_member=selected_staff).order_by(
            "-created_at"
        )

    context = {
        "staff_users": staff_users,
        "selected_staff": selected_staff,
        "labels_json": json.dumps(labels),
        "data_points_json": json.dumps(data_points),
        "is_weekend_json": json.dumps(is_weekend),
        "staff_kpi_tasks": staff_kpi_tasks,
    }

    return render(request, "kpi/management_dashboard.html", context)


@login_required
@management_or_superuser_required
def update_kpi_status(request, task_id):
    """
    Updates the status of a KPITask from the dashboard table.
    """
    if request.method == "POST":
        task = get_object_or_404(KPITask, id=task_id)
        new_status = request.POST.get("status")
        if new_status in ["Yes", "No", "Pending"]:
            task.status = new_status
            task.save()
        return redirect(f"/kpi/dashboard/?staff_id={task.staff_member.id}")
    return redirect("kpi:management_dashboard")


@login_required
@management_or_superuser_required
def download_staff_report_pdf(request, staff_id):
    """
    Generates a PDF report using WeasyPrint for a specific staff member.
    """
    staff_user = get_object_or_404(User, id=staff_id, role="Staff")

    # 1. Fetch Task History
    tasks = Task.objects.filter(assigned_to=staff_user).order_by("-created_at")[:50]

    # 2. Generate KPI Data
    today = timezone.now().date()
    kpi_data = []

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        weekday = date.weekday()
        is_wknd = weekday >= 5

        daily_tasks = KPITask.objects.filter(
            staff_member=staff_user, created_at__date=date, status__in=["Yes", "No"]
        )

        if daily_tasks.exists():
            total_score = sum(100 for t in daily_tasks if t.status == "Yes")
            avg_grade = total_score / daily_tasks.count()
            value = round(avg_grade, 1)
        else:
            value = 0

        kpi_data.append(
            {
                "label": date.strftime("%a, %b %d"),
                "value": value,
                "is_weekend": is_wknd,
            }
        )

    context = {
        "staff_user": staff_user,
        "tasks": tasks,
        "kpi_data": kpi_data,
        "now": timezone.now(),
    }

    # Render HTML template to string
    html_string = render_to_string("kpi/pdf_report.html", context)

    if HTML is None:
        return HttpResponse(
            "WeasyPrint is not installed or configured correctly.", status=500
        )

    # Generate PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    pdf = html.write_pdf(presentational_hints=True)

    # Create HttpResponse with PDF content type
    response = HttpResponse(pdf, content_type="application/pdf")
    filename = f"{staff_user.username}_Report.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


class KPITaskCreateView(LoginRequiredMixin, CreateView):
    model = KPITask
    template_name = "kpi/kpi_task_form.html"
    fields = ["title", "description", "staff_member", "status"]

    def get_success_url(self):
        # Redirect directly to the specific staff member's dashboard tab
        return f"/kpi/dashboard/?staff_id={self.object.staff_member.id}"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["staff_member"].queryset = User.objects.filter(role="Staff")
        return form

    def form_valid(self, form):
        form.instance.graded_by = self.request.user
        return super().form_valid(form)