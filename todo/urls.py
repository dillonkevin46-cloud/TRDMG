from django.urls import path
from .views import DailyTaskListView, WeeklyTaskListView, MonthlyTaskListView, TaskUpdateView, TaskCreateView

app_name = 'todo'

urlpatterns = [
    path('daily/', DailyTaskListView.as_view(), name='task-list-daily'),
    path('weekly/', WeeklyTaskListView.as_view(), name='task-list-weekly'),
    path('monthly/', MonthlyTaskListView.as_view(), name='task-list-monthly'),
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('task-create/', TaskCreateView.as_view(), name='task-create'),
]
