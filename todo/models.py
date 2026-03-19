from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

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

    due_date = models.DateTimeField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'Completed':
            return timezone.now() > self.due_date
        return False

    @property
    def is_due_soon(self):
        if self.due_date and self.status != 'Completed':
            now = timezone.now()
            return now <= self.due_date <= now + timedelta(hours=24)
        return False

    @property
    def time_taken(self):
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            parts = []
            if days > 0:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours > 0:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes > 0 or (days == 0 and hours == 0):
                parts.append(f"{minutes} min{'s' if minutes != 1 else ''}")

            return ", ".join(parts)
        return "N/A"

    def clean(self):
        super().clean()
        if self.status == 'Stuck':
            pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_task = Task.objects.get(pk=self.pk)
            old_status = old_task.status

            if self.status == 'Started' and old_status != 'Started' and not self.started_at:
                self.started_at = timezone.now()
            elif self.status == 'Completed' and old_status != 'Completed':
                self.completed_at = timezone.now()
        else:
            if self.status == 'Started':
                self.started_at = timezone.now()
            elif self.status == 'Completed':
                self.completed_at = timezone.now()

        super().save(*args, **kwargs)

        from accounts.models import Notification
        from django.urls import reverse

        link = f"/todo/{self.pk}/update/"

        if is_new:
            Notification.objects.create(
                recipient=self.assigned_to,
                message=f"New task assigned: {self.title}",
                link=link
            )
        elif old_status and old_status != self.status:
            msg = f"Task '{self.title}' status updated to {self.status}"
            Notification.objects.create(recipient=self.created_by, message=msg, link=link)
            if self.created_by != self.assigned_to:
                Notification.objects.create(recipient=self.assigned_to, message=msg, link=link)

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            from accounts.models import Notification
            link = f"/todo/{self.task.pk}/update/"
            msg = f"New comment on '{self.task.title}'"

            if self.user != self.task.assigned_to:
                Notification.objects.create(recipient=self.task.assigned_to, message=msg, link=link)
            if self.user != self.task.created_by and self.task.assigned_to != self.task.created_by:
                Notification.objects.create(recipient=self.task.created_by, message=msg, link=link)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"
