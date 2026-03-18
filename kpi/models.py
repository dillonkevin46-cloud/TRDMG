from django.db import models
from django.conf import settings

class KPITask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kpi_tasks',
        limit_choices_to={'role': 'Staff'}
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_kpis',
        limit_choices_to={'role': 'Management'}
    )
    grade = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KPI: {self.title} for {self.staff_member.username}"
