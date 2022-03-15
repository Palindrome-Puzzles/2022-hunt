from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from spoilr.core.models import Team, alpha_validator

from ..models import TeamRegistrationInfo

class RegisterTeamForm(forms.ModelForm):
    class Meta:
        model = TeamRegistrationInfo
        fields = [
            'team_name', 'team_email', 'team_emoji', 'team_username', 'team_password1', 'team_password2',
            'captain_name', 'captain_pronouns', 'captain_email', 'captain_phone',
            'bg_bio', 'bg_style', 'bg_win', 'bg_first_year', 'bg_started', 'bg_location', 'bg_comm',
            'size_total', 'size_last_year', 'size_undergrads', 'size_grads', 'size_alumni', 'size_faculty', 'size_minors',
            'other_unattached', 'other_workshop', 'other_puzzle_club', 'other_how',
            'other',
        ]
        widgets = {
            'bg_bio': forms.Textarea(),
            'other': forms.Textarea(),
        }

    team_name = forms.CharField(label='Team Name', max_length=200, widget=forms.TextInput(attrs={'autofocus': True}))
    # Note: team_username is special-cased in the template.
    team_username = forms.CharField(label='Username', max_length=50, widget=forms.TextInput(attrs={'pattern': '[A-Za-z]+', 'autocomplete': 'username'}), validators=[alpha_validator])
    team_username.help_text = 'If your team name contains numbers, symbols, emoji, or other special characters, please provide a version of your team name that only uses the letters A-Z. If your team name does not contain any of the above, please enter your team name as typed above.'
    team_password1 = forms.CharField(label='Team Password', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    team_password1.help_text = 'The password should be at least 8 characters in length, and different from your username.'
    team_password2 = forms.CharField(label='Team Password (confirm)', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    team_password2.help_text = 'You should share this password with your team to log in.'

    captain_name = forms.CharField(label='Name', max_length=200)
    captain_email = forms.EmailField(label='E-mail', max_length=200)

    def for_update(self):
        self.fields['team_username'].widget.attrs['disabled'] = True
        self.fields['team_password1'].required = False
        self.fields['team_password2'].required = False

    def for_locked(self):
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = True

    def clean_team_username(self):
        team_username = self.cleaned_data.get('team_username')
        if team_username:
            existing_team_with_username = Team.objects.filter(username__iexact=team_username).first()
            if existing_team_with_username:
                if not self.instance or self.instance.team_id != existing_team_with_username.id:
                    raise ValidationError('That username is already taken', code='team_username_taken')
        return team_username

    def clean_team_name(self):
        team_name = self.cleaned_data.get('team_name')
        if team_name:
            existing_team_with_name = Team.objects.filter(name__iexact=team_name).first()
            if existing_team_with_name:
                if not self.instance or self.instance.team_id != existing_team_with_name.id:
                    raise ValidationError('That name is already taken', code='team_name_taken')
        return team_name

    def clean_team_password2(self):
        password1 = self.cleaned_data.get("team_password1")
        password2 = self.cleaned_data.get("team_password2")
        if (password1 or password2) and password1 != password2:
            raise ValidationError(
                'The two password fields didn’t match.',
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()

        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('team_password2')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                self.add_error('team_password2', error)
