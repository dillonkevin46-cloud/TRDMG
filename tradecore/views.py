import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from todo.models import Task

@login_required
def index(request):
    user = request.user
    context = {}

    if user.role in ['Management', 'Superuser']:
        if user.is_superuser:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(created_by=user)

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='Completed').count()
        stuck_tasks = tasks.filter(status='Stuck').count()
        not_started = tasks.filter(status='Not Started').count()
        started = tasks.filter(status='Started').count()

        status_labels = ['Not Started', 'Started', 'Completed', 'Stuck']
        status_counts = [not_started, started, completed_tasks, stuck_tasks]

        context['total_tasks'] = total_tasks
        context['completed_tasks'] = completed_tasks
        context['stuck_tasks'] = stuck_tasks
        context['status_labels_json'] = json.dumps(status_labels)
        context['status_counts_json'] = json.dumps(status_counts)

        # CRITICAL FIX: Find tasks scheduled for today (or earlier) that are not completed
        context['tasks_due_today'] = tasks.filter(
            due_date__date__lte=timezone.now().date()
        ).exclude(status='Completed').order_by('due_date')

    return render(request, "dashboard.html", context)