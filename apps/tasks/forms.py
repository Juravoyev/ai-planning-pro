from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'priority', 'status', 'category',
                  'due_date', 'due_time', 'estimated_minutes', 'goal')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vazifa nomi...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Tavsif (ixtiyoriy)...'
            }),
            'priority': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'due_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time'
            }),
            'estimated_minutes': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Masalan: 30'
            }),
            'goal': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from apps.goals.models import Goal
            self.fields['goal'].queryset = Goal.objects.filter(
                user=user,
                status__in=['pending', 'in_progress']
            )
        self.fields['goal'].required = False
        self.fields['goal'].empty_label = "Maqsad tanlang (ixtiyoriy)"
