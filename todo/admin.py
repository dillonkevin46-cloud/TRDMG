from django.contrib import admin
from .models import Task, Comment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'created_by', 'created_at')
    list_filter = ('status', 'assigned_to', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('started_at', 'completed_at', 'created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('user', 'task', 'created_at')
    search_fields = ('text', 'user__username', 'task__title')
    ordering = ('-created_at',)
