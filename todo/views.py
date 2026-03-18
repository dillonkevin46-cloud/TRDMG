from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Task
from .forms import TaskStatusUpdateForm
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
                return qs
            return qs.none()

        return qs

class DailyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_daily.html'

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        # Daily: Tasks created today or active tasks (not completed) that are due/started.
        # Filtering by tasks updated or started today as an example of "Daily" relevance.
        return qs.filter(updated_at__date=today)

class WeeklyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_weekly.html'

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return qs.filter(updated_at__date__gte=start_of_week, updated_at__date__lte=end_of_week)

class MonthlyTaskListView(BaseTaskListView):
    template_name = 'todo/task_list_monthly.html'

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone.now().date()
        return qs.filter(updated_at__year=today.year, updated_at__month=today.month)

class TaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskStatusUpdateForm
    template_name = 'todo/task_update.html'
    success_url = reverse_lazy('todo:task-list-daily') # Redirect back to daily view

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
        # Override save to pass the user to the form so comment can have the author
        self.object = form.save(user=self.request.user)
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'todo/task_form.html'
    fields = ['title', 'description', 'status', 'assigned_to']
    success_url = reverse_lazy('todo:task-list-daily')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['assigned_to'].queryset = User.objects.filter(role='Staff')
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
