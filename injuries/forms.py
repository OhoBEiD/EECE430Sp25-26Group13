from django import forms
from .models import Injury


class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = [
            'player', 'injury_type', 'body_part', 'severity',
            'date_reported', 'expected_return', 'status',
            'medical_notes', 'reported_by',
        ]
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'injury_type': forms.Select(attrs={'class': 'form-control'}),
            'body_part': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'date_reported': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_return': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'reported_by': forms.TextInput(attrs={'class': 'form-control'}),
        }
