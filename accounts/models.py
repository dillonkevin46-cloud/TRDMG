from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Superuser', 'Superuser'),
        ('Management', 'Management'),
        ('Staff', 'Staff'),
        ('Viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Viewer')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
