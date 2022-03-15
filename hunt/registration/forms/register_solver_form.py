from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from spoilr.core.models import Team

from ..models import UnattachedSolverRegistrationInfo

class RegisterSolverForm(forms.ModelForm):
    class Meta:
        model = UnattachedSolverRegistrationInfo
        fields = [
            'first_name', 'last_name', 'pronouns', 'email',
            'bg_mitmh', 'bg_puzzles', 'bg_style', 'bg_prefs', 'bg_age', 'bg_mit',
            'other',
        ]
        widgets = {
            'bg_mitmh': forms.Textarea(),
            'bg_puzzles': forms.Textarea(),
            'bg_prefd': forms.Textarea(),
            'bg_mit': forms.Textarea(),
            'other': forms.Textarea(),
        }
