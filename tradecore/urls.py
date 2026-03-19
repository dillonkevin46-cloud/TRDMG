"""
URL configuration for tradecore project.
"""

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("admin/", admin.site.urls),
    path("todo/", include("todo.urls")),
    path("accounts/", include("accounts.urls")),
    
    # CRITICAL FIX: Must be accounts/ so Django can find the login template!
    path("accounts/", include("django.contrib.auth.urls")), 
    
    path("kpi/", include("kpi.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
]
