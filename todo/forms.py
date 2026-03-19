from django import forms
from .models import Task, Comment

class TaskForm(forms.ModelForm):
    comment_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5',
            'rows': 3
        }),
        help_text="Required if status is 'Stuck'."
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'description': forms.Textarea(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'status': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'due_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].required = False

        if self.instance and self.instance.pk:
            self.fields['assigned_to'].required = False
            self.fields['title'].required = False
            self.fields['description'].required = False

    def clean(self):
        cleaned_data = super().clean()

        if self.instance and self.instance.pk:
            if not cleaned_data.get('assigned_to'):
                cleaned_data['assigned_to'] = self.instance.assigned_to
            if not cleaned_data.get('title'):
                cleaned_data['title'] = self.instance.title
            if not cleaned_data.get('description'):
                cleaned_data['description'] = self.instance.description

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
