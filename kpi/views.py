from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from accounts.decorators import management_or_superuser_required
from .models import KPITask
from todo.models import Task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
import random
import json

# We catch OSError here because Windows throws it when GTK3 is missing
try:
    from weasyprint import HTML, CSS
except (ImportError, OSError):
    HTML = None

User = get_user_model()

@login_required
@management_or_superuser_required
def management_dashboard(request):
    """
    Management Dashboard showing KPIs for Staff members.
    For this example, we generate dummy daily KPI data for a specific staff member
    to demonstrate the Chart.js integration separating weekends from weekdays.
    """
    staff_users = User.objects.filter(role='Staff')
    selected_staff_id = request.GET.get('staff_id')

    if selected_staff_id:
        selected_staff = User.objects.filter(id=selected_staff_id, role='Staff').first()
    else:
        selected_staff = staff_users.first()

    # Generate past 14 days of data
    today = timezone.now().date()
    labels = []
    data_points = []
    is_weekend = []

    # Example logic: Random KPI scores (or query actual KPITask objects)
    # We will simulate data for demonstration of the UI requirements
    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        # 0 = Monday, 6 = Sunday
        weekday = date.weekday()

        labels.append(date.strftime("%a, %b %d"))
        is_wknd = weekday >= 5
        is_weekend.append(is_wknd)

        # Query actual KPITask data
        if selected_staff:
            daily_tasks = KPITask.objects.filter(
                staff_member=selected_staff,
                created_at__date=date
            ).exclude(grade__isnull=True)

            if daily_tasks.exists():
                avg_grade = sum(t.grade for t in daily_tasks) / daily_tasks.count()
                data_points.append(round(avg_grade, 1))
            else:
                data_points.append(0)
        else:
            data_points.append(0)

    context = {
        'staff_users': staff_users,
        'selected_staff': selected_staff,
        'labels_json': json.dumps(labels),
        'data_points_json': json.dumps(data_points),
        'is_weekend_json': json.dumps(is_weekend),
    }

    return render(request, 'kpi/management_dashboard.html', context)

@login_required
@management_or_superuser_required
def download_staff_report_pdf(request, staff_id):
    """
    Generates a PDF report using WeasyPrint for a specific staff member.
    Includes Task History and KPI Graph data.
    """
    staff_user = get_object_or_404(User, id=staff_id, role='Staff')

    # 1. Fetch Task History
    tasks = Task.objects.filter(assigned_to=staff_user).order_by('-created_at')[:50]

    # 2. Generate KPI Data
    today = timezone.now().date()
    kpi_data = []

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        weekday = date.weekday()

        is_wknd = weekday >= 5

        daily_tasks = KPITask.objects.filter(
            staff_member=staff_user,
            created_at__date=date
        ).exclude(grade__isnull=True)

        if daily_tasks.exists():
            avg_grade = sum(t.grade for t in daily_tasks) / daily_tasks.count()
            value = round(avg_grade, 1)
        else:
            value = 0

        kpi_data.append({
            'label': date.strftime("%a, %b %d"),
            'value': value,
            'is_weekend': is_wknd
        })

    context = {
        'staff_user': staff_user,
        'tasks': tasks,
        'kpi_data': kpi_data,
        'now': timezone.now(),
    }

    # Render HTML template to string
    html_string = render_to_string('kpi/pdf_report.html', context)

    # Check if WeasyPrint loaded successfully
    if HTML is None:
        return HttpResponse("WeasyPrint is not installed or configured correctly on this Windows Server. Please install the GTK3 Runtime.", status=500)

    # Generate PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf(presentational_hints=True)

    # Create HttpResponse with PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"{staff_user.username}_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response