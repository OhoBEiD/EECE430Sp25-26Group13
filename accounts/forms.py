from django import forms

from .models import UserProfile


class RoleAssignmentForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'linked_player']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'linked_player': forms.Select(attrs={'class': 'form-control'}),
        }
