from django.urls import path
from . import views

app_name = 'kpi'

urlpatterns = [
    path('dashboard/', views.management_dashboard, name='management_dashboard'),
]
