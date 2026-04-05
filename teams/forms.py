from django import forms
from .models import Team, Event


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'age_group', 'coach_name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age_group': forms.Select(attrs={'class': 'form-control'}),
            'coach_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'date', 'start_time', 'end_time', 'location', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
