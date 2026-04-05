from django import forms
from .models import PlayerStats


class StatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        exclude = ['player']
        widgets = {
            'date_recorded': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'serve_accuracy': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'spike_success': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'block_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'dig_success': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'set_accuracy': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'receive_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'max': 100,
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this session...',
            }),
        }
