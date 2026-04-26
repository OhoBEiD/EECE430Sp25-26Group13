from django import forms
from django.contrib.auth.models import User

from accounts.roles import Role

from .models import Event, Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'age_group', 'coach', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age_group': forms.Select(attrs={'class': 'form-control'}),
            'coach': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coach'].queryset = User.objects.filter(profile__role=Role.COACH).order_by('username')
        self.fields['coach'].required = False
        self.fields['coach'].empty_label = '— Unassigned —'
        # Coach (when editing their own team) can adjust description but not reassign the coach FK.
        if user is not None and not (user.is_superuser or getattr(user, 'profile', None) and user.profile.role in (Role.MANAGER, Role.ADMIN)):
            self.fields['coach'].disabled = True


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
