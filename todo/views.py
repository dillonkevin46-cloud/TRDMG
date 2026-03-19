from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Task
from .forms import TaskForm
from django.contrib.auth import get_user_model

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

        search_query = self.request.GET.get('search')
        if search_query:
            qs = qs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
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
