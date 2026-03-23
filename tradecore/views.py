from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from todo.models import Task
import json

@login_required
def index(request):
    user = request.user
    context = {}

    if user.role in ['Management', 'Superuser'] or user.is_superuser:
        if user.is_superuser:
            tasks = Task.objects.all()
            tasks_due_today = Task.objects.filter(due_date__date=timezone.now().date()).exclude(status='Completed')
        else:
            tasks = Task.objects.filter(created_by=user)
            tasks_due_today = Task.objects.filter(created_by=user, due_date__date=timezone.now().date()).exclude(status='Completed')

        total_tasks = tasks.count()

        # Calculate counts for the 4 statuses
        not_started = tasks.filter(status='Not Started').count()
        started = tasks.filter(status='Started').count()
        completed = tasks.filter(status='Completed').count()
        stuck = tasks.filter(status='Stuck').count()

        status_labels = ['Not Started', 'Started', 'Completed', 'Stuck']
        status_counts = [not_started, started, completed, stuck]

        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed,
            'stuck_tasks': stuck,
            'status_labels_json': json.dumps(status_labels),
            'status_counts_json': json.dumps(status_counts),
            'tasks_due_today': tasks_due_today,
        }

    return render(request, 'dashboard.html', context)
