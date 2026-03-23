from django.urls import path
from . import views

app_name = 'kpi'

urlpatterns = [
    path('dashboard/', views.management_dashboard, name='management_dashboard'),
    path('objective/add/', views.KPIObjectiveCreateView.as_view(), name='objective_create'),
    path('evaluate/add/', views.KPIEvaluationCreateView.as_view(), name='evaluation_create'),
    path('staff/<int:staff_id>/report/', views.download_staff_report_pdf, name='download_staff_report_pdf'),
]
