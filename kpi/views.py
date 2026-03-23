from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from accounts.decorators import management_or_superuser_required
from .models import KPIObjective, KPIEvaluation
from todo.models import Task
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
import json

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
    Calculates averages for a Radar/Spider chart based on KPIObjectives and KPIEvaluations.
    """
    staff_users = User.objects.filter(role='Staff')
    selected_staff_id = request.GET.get('staff_id')

    if selected_staff_id:
        selected_staff = User.objects.filter(id=selected_staff_id, role='Staff').first()
    else:
        selected_staff = staff_users.first()

    objectives = KPIObjective.objects.all()

    radar_labels = []
    radar_data = []

    for obj in objectives:
        radar_labels.append(obj.title)

        if selected_staff:
            evals = KPIEvaluation.objects.filter(objective=obj, staff_member=selected_staff)
            if evals.exists():
                # Average the score_value (10, 7, 5, 3, 0)
                total_score = sum(e.score_value for e in evals)
                avg_score = total_score / evals.count()
                radar_data.append(round(avg_score, 1))
            else:
                radar_data.append(0)
        else:
            radar_data.append(0)

    # Fetch evaluation history for the table
    recent_evaluations = None
    if selected_staff:
        recent_evaluations = KPIEvaluation.objects.filter(staff_member=selected_staff).order_by('-date', '-created_at')[:20]

    context = {
        'staff_users': staff_users,
        'selected_staff': selected_staff,
        'radar_labels_json': json.dumps(radar_labels),
        'radar_data_json': json.dumps(radar_data),
        'recent_evaluations': recent_evaluations,
        'objectives': objectives,
    }

    return render(request, 'kpi/management_dashboard.html', context)


@login_required
@management_or_superuser_required
def download_staff_report_pdf(request, staff_id):
    """
    Generates a PDF report using WeasyPrint for a specific staff member.
    Includes Task History and KPI Graph data (Evaluations).
    """
    staff_user = get_object_or_404(User, id=staff_id, role='Staff')

    # 1. Fetch Task History
    tasks = Task.objects.filter(assigned_to=staff_user).order_by('-created_at')[:50]

    # 2. Fetch KPI Evaluations
    evaluations = KPIEvaluation.objects.filter(staff_member=staff_user).order_by('-date', '-created_at')[:50]

    # Calculate objective averages for the PDF summary
    objectives = KPIObjective.objects.all()
    objective_summaries = []

    for obj in objectives:
        obj_evals = KPIEvaluation.objects.filter(objective=obj, staff_member=staff_user)
        if obj_evals.exists():
            avg_score = sum(e.score_value for e in obj_evals) / obj_evals.count()
            # Normalize to 100 for the CSS bar chart in the PDF (Max score is 10)
            percentage = min(avg_score * 10, 100)
            objective_summaries.append({
                'label': obj.title,
                'value': round(percentage, 1),
                'is_weekend': False # Reuse existing template logic, or update template
            })
        else:
            objective_summaries.append({
                'label': obj.title,
                'value': 0,
                'is_weekend': False
            })

    context = {
        'staff_user': staff_user,
        'tasks': tasks,
        'evaluations': evaluations,
        'kpi_data': objective_summaries, # Reuse existing variable name for the PDF template chart
        'now': timezone.now(),
    }

    # Render HTML template to string
    html_string = render_to_string('kpi/pdf_report.html', context)

    if HTML is None:
        return HttpResponse("WeasyPrint is not installed or configured correctly on this system.", status=500)

    # Generate PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    # Use presentational_hints=True to process basic HTML attributes like bgcolor if any
    pdf = html.write_pdf(presentational_hints=True)

    # Create HttpResponse with PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    # Set Content-Disposition to force download with specific filename
    filename = f"{staff_user.username}_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


class KPIObjectiveCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = KPIObjective
    template_name = 'kpi/kpi_task_form.html'
    from .forms import KPIObjectiveForm
    form_class = KPIObjectiveForm
    success_url = reverse_lazy('kpi:management_dashboard')

    def test_func(self):
        return self.request.user.role == 'Management' or self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class KPIEvaluationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = KPIEvaluation
    template_name = 'kpi/kpi_task_form.html'
    from .forms import KPIEvaluationForm
    form_class = KPIEvaluationForm
    success_url = reverse_lazy('kpi:management_dashboard')

    def test_func(self):
        return self.request.user.role == 'Management' or self.request.user.is_superuser

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['staff_member'].queryset = User.objects.filter(role='Staff')
        return form

    def form_valid(self, form):
        form.instance.evaluated_by = self.request.user
        return super().form_valid(form)
