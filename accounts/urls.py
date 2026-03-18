from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('settings/', views.settings_dashboard, name='settings_dashboard'),

    # Staff routes
    path('settings/staff/add/', views.add_staff, name='add_staff'),
    path('settings/staff/<int:user_id>/edit/', views.edit_staff, name='edit_staff'),
    path('settings/staff/<int:user_id>/remove/', views.remove_staff, name='remove_staff'),
    path('settings/staff/<int:user_id>/reset_password/', views.reset_staff_password, name='reset_staff_password'),

    # Department routes
    path('settings/department/add/', views.add_department, name='add_department'),
    path('settings/department/<int:dept_id>/edit/', views.edit_department, name='edit_department'),
    path('settings/department/<int:dept_id>/remove/', views.remove_department, name='remove_department'),
]
