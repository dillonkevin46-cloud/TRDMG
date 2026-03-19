from django import forms
from .models import KPIObjective, KPIEvaluation

class KPIObjectiveForm(forms.ModelForm):
    class Meta:
        model = KPIObjective
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'description': forms.Textarea(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5', 'rows': 4}),
        }

class KPIEvaluationForm(forms.ModelForm):
    class Meta:
        model = KPIEvaluation
        fields = ['objective', 'staff_member', 'date', 'score', 'reason']
        widgets = {
            'objective': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'staff_member': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'score': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5'}),
            'reason': forms.Textarea(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-4 py-2.5', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get('score')
        reason = cleaned_data.get('reason')

        if score in ['Bad', 'Very Bad'] and not reason:
            self.add_error('reason', "A reason MUST be provided when scoring below Normal.")

        return cleaned_data
