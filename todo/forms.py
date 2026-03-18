from django import forms
from .models import Task, Comment

class TaskStatusUpdateForm(forms.ModelForm):
    comment_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Required if status is 'Stuck'."
    )

    class Meta:
        model = Task
        fields = ['status']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment_text = cleaned_data.get('comment_text')

        # Business Logic Constraint: Comment is mandatory when status is 'Stuck'
        if status == 'Stuck' and not comment_text:
            self.add_error('comment_text', 'A comment MUST be provided when changing a task to "Stuck".')

        return cleaned_data

    def save(self, commit=True, user=None):
        task = super().save(commit=False)
        comment_text = self.cleaned_data.get('comment_text')

        if commit:
            task.save()
            if comment_text and user:
                Comment.objects.create(task=task, user=user, text=comment_text)

        return task
