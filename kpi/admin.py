from django.contrib import admin
from .models import KPIObjective, KPIEvaluation

@admin.register(KPIObjective)
class KPIObjectiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')

@admin.register(KPIEvaluation)
class KPIEvaluationAdmin(admin.ModelAdmin):
    list_display = ('objective', 'staff_member', 'evaluated_by', 'score', 'date')
    list_filter = ('staff_member', 'evaluated_by', 'score', 'date')
    search_fields = ('objective__title', 'staff_member__username', 'evaluated_by__username', 'reason')
