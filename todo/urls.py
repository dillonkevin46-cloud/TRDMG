from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('daily/', views.DailyTaskListView.as_view(), name='task-list-daily'),
    path('weekly/', views.WeeklyTaskListView.as_view(), name='task-list-weekly'),
    path('monthly/', views.MonthlyTaskListView.as_view(), name='task-list-monthly'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('task-create/', views.TaskCreateView.as_view(), name='task-create'),
    path('board/', views.TaskBoardView.as_view(), name='task-board'),
    path('<int:pk>/update-status-ajax/', views.update_task_status_ajax, name='task-update-status-ajax'),
    path('notes/', views.personal_notes_view, name='personal-notes'),
    path('notes/<int:note_id>/toggle/', views.toggle_note_status, name='toggle-note'),
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete-note'),
]
