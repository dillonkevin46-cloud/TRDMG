from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from .models import Department

User = get_user_model()

class StaffUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'department', 'manager']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow managers to be assigned
        self.fields['manager'].queryset = User.objects.filter(role='Management')

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
