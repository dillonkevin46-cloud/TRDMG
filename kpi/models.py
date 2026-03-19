from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class KPIObjective(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class KPIEvaluation(models.Model):
    SCORE_CHOICES = [
        ('Great', 'Great'),
        ('Good', 'Good'),
        ('Normal', 'Normal'),
        ('Bad', 'Bad'),
        ('Very Bad', 'Very Bad'),
    ]

    objective = models.ForeignKey(KPIObjective, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations',
        limit_choices_to={'role': 'Staff'}
    )
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluator_records',
        limit_choices_to={'role': 'Management'}
    )
    date = models.DateField(default=timezone.now)
    score = models.CharField(max_length=20, choices=SCORE_CHOICES)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.score in ['Bad', 'Very Bad'] and not self.reason:
            raise ValidationError("A reason MUST be provided when scoring below Normal.")

    @property
    def score_value(self):
        mapping = {
            'Great': 10,
            'Good': 7,
            'Normal': 5,
            'Bad': 3,
            'Very Bad': 0,
        }
        return mapping.get(self.score, 0)

    def __str__(self):
        return f"{self.staff_member.username} - {self.objective.title} ({self.score})"
