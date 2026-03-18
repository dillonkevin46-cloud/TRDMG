from django.contrib import admin
from .models import KPITask

@admin.register(KPITask)
class KPITaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'staff_member', 'graded_by', 'status', 'created_at')
    list_filter = ('staff_member', 'graded_by', 'status', 'created_at')
    search_fields = ('title', 'description', 'staff_member__username', 'graded_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
