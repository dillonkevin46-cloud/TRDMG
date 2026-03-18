from django.urls import path
from . import views

app_name = 'kpi'

urlpatterns = [
    path('dashboard/', views.management_dashboard, name='management_dashboard'),
    path('report/<int:staff_id>/pdf/', views.download_staff_report_pdf, name='download_staff_report_pdf'),
    path('task-create/', views.KPITaskCreateView.as_view(), name='task-create'),
]
