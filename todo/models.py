from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class Task(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('Started', 'Started'),
        ('Completed', 'Completed'),
        ('Stuck', 'Stuck'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'Staff'}
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        limit_choices_to={'role': 'Management'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.status == 'Stuck':
            # Check if there are any comments when saving
            # This validation is better suited for a Form as comments are related objects
            # but providing a hook here for completeness if needed.
            # We'll rely on the Form to enforce this business logic fully before saving.
            pass

    def save(self, *args, **kwargs):
        # Time tracking logic based on status changes
        if self.pk:
            orig = Task.objects.get(pk=self.pk)
            # If changing to Started from something else
            if self.status == 'Started' and orig.status != 'Started':
                if not self.started_at:
                    self.started_at = timezone.now()
            # If changing to Completed from something else
            elif self.status == 'Completed' and orig.status != 'Completed':
                self.completed_at = timezone.now()
        else:
            # New object creation
            if self.status == 'Started':
                self.started_at = timezone.now()
            elif self.status == 'Completed':
                self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"
