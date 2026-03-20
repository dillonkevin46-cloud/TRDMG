from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, UpdateView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Task, PersonalNote
from .forms import TaskForm
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class BaseTaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Role-based visibility
        if user.role == 'Staff':
            qs = qs.filter(assigned_to=user)
        elif user.role == 'Management':
            # Management sees tasks created by them, or tasks assigned to staff they manage.
            qs = qs.filter(Q(created_by=user) | Q(assigned_to__manager=user))
        else:
            # For Viewer/Superuser, show none or all depending on specs (Assuming empty for unauthorized roles)
            if user.is_superuser:
                pass
            else:
                qs = qs.none()

        search = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if status_filter and status_filter != 'All':
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', 'All')
        return context

class DailyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_daily.html'

    def get_queryset(self):
        qs = super().get_queryset()

        date_str = self.request.GET.get('date')
        if date_str:
            try:
                from datetime import datetime
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        return qs.filter(
            Q(due_date__date=selected_date) |
            Q(due_date__isnull=True, created_at__date=selected_date)
        ).order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_str = self.request.GET.get('date')
        if date_str:
            try:
                from datetime import datetime
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        context['selected_date'] = selected_date

        # Split the context data into active and completed
        tasks = context['tasks']
        context['active_tasks'] = tasks.exclude(status='Completed')
        context['completed_tasks'] = tasks.filter(status='Completed')

        return context

class WeeklyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_weekly.html'

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return qs.filter(
            Q(due_date__date__gte=start_of_week, due_date__date__lte=end_of_week) |
            Q(due_date__isnull=True, created_at__date__gte=start_of_week, created_at__date__lte=end_of_week)
        ).order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = context['tasks']
        context['active_tasks'] = tasks.exclude(status='Completed')
        context['completed_tasks'] = tasks.filter(status='Completed')
        return context

class MonthlyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_monthly.html'

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        return qs.filter(
            Q(due_date__year=today.year, due_date__month=today.month) |
            Q(due_date__isnull=True, created_at__year=today.year, created_at__month=today.month)
        ).order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = context['tasks']
        context['active_tasks'] = tasks.exclude(status='Completed')
        context['completed_tasks'] = tasks.filter(status='Completed')
        return context

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'todo/task_update.html'
    success_url = reverse_lazy('todo:task-list-daily')

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Role-based visibility
        if user.role == 'Staff':
            qs = qs.filter(assigned_to=user)
        elif user.role == 'Management':
            qs = qs.filter(Q(created_by=user) | Q(assigned_to__manager=user))
        else:
            if user.is_superuser:
                return qs
            return qs.none()

        return qs

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

@login_required
def personal_notes_view(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            PersonalNote.objects.create(user=request.user, text=text)
        return redirect('todo:personal-notes')

    notes = PersonalNote.objects.filter(user=request.user).order_by('is_completed', '-created_at')
    return render(request, 'todo/note_list.html', {'notes': notes})

@login_required
@require_POST
def toggle_note_status(request, note_id):
    note = get_object_or_404(PersonalNote, id=note_id, user=request.user)
    note.is_completed = not note.is_completed
    note.save()
    return JsonResponse({'success': True, 'is_completed': note.is_completed})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(PersonalNote, id=note_id, user=request.user)
    note.delete()
    return redirect('todo:personal-notes')

class TaskBoardView(LoginRequiredMixin, TemplateView):
    template_name = 'todo/task_board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        qs = Task.objects.all()
        # Role-based visibility
        if user.role == 'Staff':
            qs = qs.filter(assigned_to=user)
        elif user.role == 'Management':
            qs = qs.filter(Q(created_by=user) | Q(assigned_to__manager=user))
        else:
            if not user.is_superuser:
                qs = qs.none()

        search = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if status_filter and status_filter != 'All':
            qs = qs.filter(status=status_filter)

        context['not_started_tasks'] = qs.filter(status='Not Started').order_by('due_date')
        context['started_tasks'] = qs.filter(status='Started').order_by('due_date')
        context['stuck_tasks'] = qs.filter(status='Stuck').order_by('due_date')
        context['completed_tasks'] = qs.filter(status='Completed').order_by('-completed_at')

        context['search'] = search if search else ''
        context['status_filter'] = status_filter if status_filter else 'All'

        return context

@login_required
@require_POST
def update_task_status_ajax(request, pk):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status in dict(Task._meta.get_field('status').choices):
            task = get_object_or_404(Task, pk=pk)

            # Additional security: verify user can edit this task
            user = request.user
            can_edit = False
            if user.is_superuser:
                can_edit = True
            elif user.role == 'Staff' and task.assigned_to == user:
                can_edit = True
            elif user.role == 'Management' and (task.created_by == user or (task.assigned_to and task.assigned_to.manager == user)):
                can_edit = True

            if can_edit:
                task.status = new_status
                task.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'todo/task_form.html'
    form_class = TaskForm
    success_url = reverse_lazy('todo:task-list-daily')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['assigned_to'].queryset = User.objects.filter(role='Staff')
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save(user=self.request.user)
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())
