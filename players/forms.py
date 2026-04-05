from django import forms
from .models import VolleyPlayer


class PlayerForm(forms.ModelForm):
    class Meta:
        model = VolleyPlayer
        fields = ['name', 'date_joined', 'position', 'salary', 'contact_person', 'team']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'position': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Position'),
                ('Setter', 'Setter'),
                ('Outside Hitter', 'Outside Hitter'),
                ('Middle Blocker', 'Middle Blocker'),
                ('Opposite Hitter', 'Opposite Hitter'),
                ('Libero', 'Libero'),
                ('Defensive Specialist', 'Defensive Specialist'),
            ]),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'team': forms.Select(attrs={'class': 'form-control'}),
        }
