import re

import emoji

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe

from spoilr.core.models import Team

MAX_EMOJIS = 5
COARSE_EMOJI_RE = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002500-\U00002BEF"  # chinese char
    u"\U00002702-\U000027B0"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U00010000-\U0010ffff"
    u"\u2640-\u2642"
    u"\u2600-\u2B55"
    u"\u200d"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\ufe0f"  # dingbats
    u"\u3030"
"]+", re.UNICODE)

class UserAuth(models.Model):
    """Authentication metadata for users."""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)
    delete_time = models.DateTimeField(blank=True, null=True)

class TeamRegistrationInfo(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)

    team_email = models.EmailField(verbose_name='Team E-mail', max_length=200, null=True, blank=True)
    team_emoji = models.CharField(verbose_name='Team Emoji', max_length=50, null=True, blank=True)
    team_emoji.help_text = 'This will be displayed publicly to all other teams.'

    captain_pronouns = models.CharField(verbose_name='Pronouns', max_length=50, null=True, blank=True)
    captain_phone = models.CharField(verbose_name='Phone', max_length=50)

    bg_bio = models.CharField(verbose_name='Team Bio', max_length=1500, default='')
    bg_bio.help_text ='This will be displayed publicly to all other teams.'
    bg_style = models.CharField(max_length=20, verbose_name='What describes your team’s style of playing?', choices=(('fun', 'We’re playing for fun!'), ('compete', 'We’re pretty into puzzles but we’re not so focused on winning.'), ('win', 'We hope to see the entire hunt and maybe find the coin.')), default='fun')
    bg_win = models.CharField(max_length=20, verbose_name='Is your team hoping to win the hunt?', choices=(('yes', 'Yes'), ('no', 'No'), ('unsure', 'Unsure')), default='unsure')
    bg_win.help_text = 'Teams are strongly encouraged to have active MIT students on their team because Mystery Hunt is an MIT event. At least 2 MIT students are required to write the hunt.'
    bg_first_year = models.CharField(verbose_name='In which year was your team members’ earliest experience of the MIT Mystery Hunt?', max_length=200, default='')
    bg_started = models.CharField(verbose_name='When was your team established?', max_length=200, default='')
    bg_location = models.CharField(verbose_name='Where are your team members located?', max_length=200, default='')
    bg_comm = models.CharField(verbose_name='What communication application will you be using to communicate with your team members while solving the MIT Mystery Hunt this year?', max_length=200, default='')

    size_total = models.IntegerField(verbose_name='How many people are on your team in total?', default=0)
    size_last_year = models.IntegerField(verbose_name='How many people were on your team last year?', default=0)
    size_undergrads = models.IntegerField(verbose_name='How many MIT undergraduates?', default=0)
    size_grads = models.IntegerField(verbose_name='How many MIT graduate students?', default=0)
    size_alumni = models.IntegerField(verbose_name='How many MIT alumni?', default=0)
    size_faculty = models.IntegerField(verbose_name='How many members from MIT faculty and staff?', default=0)
    size_minors = models.IntegerField(verbose_name='How many minors (under 18 during Hunt)?', default=0)

    other_unattached = models.CharField(max_length=20, verbose_name='Are you willing to enlist unattached solvers?', choices=(('', ''), ('yes', 'Yes'), ('no', 'No')), default='')
    other_workshop = models.CharField(max_length=20, verbose_name='Would your team like to participate in the How to Hunt workshop prior to the event?', choices=(('', ''), ('yes', 'Yes'), ('no', 'No')), default='')
    other_puzzle_club = models.CharField(max_length=20, verbose_name='Do you have members from the MIT Puzzle Club on your team?', choices=(('', ''), ('yes', 'Yes'), ('no', 'No')), default='')
    other_how = models.CharField(max_length=20, verbose_name='How did you hear about the MIT Mystery Hunt?', choices=(('', ''), ('past', 'We’ve played in the past'), ('group', 'Through a puzzle interest group (e.g. National Puzzlers’ League)'), ('word-of-mouth', 'Word of mouth from past participants or organizers'), ('social', 'Through e-mail or social media'), ('puzzle-club', 'Through the MIT Puzzle Club'), ('other', 'Other')), default='')

    other = models.CharField(verbose_name='Anything else you’d like to share with us? Comments, questions, puns?', max_length=1500, null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def display_emoji(self):
        if self.team_emoji:
            replaced = emoji.emojize(escape(self.team_emoji), use_aliases=True)
            emojis_only = ''.join([c for c in replaced if c in emoji.UNICODE_EMOJI or COARSE_EMOJI_RE.match(c)][:MAX_EMOJIS])
            return mark_safe(emojis_only)
        return ''

class UnattachedSolverRegistrationInfo(models.Model):
    first_name = models.CharField(verbose_name='First (Given) Name or Nickname', max_length=200)
    last_name = models.CharField(verbose_name='Last Name', max_length=200)
    pronouns = models.CharField(verbose_name='Pronouns', max_length=50, null=True, blank=True)
    email = models.EmailField(verbose_name='E-mail', max_length=200)

    bg_mitmh = models.CharField(verbose_name='Have you participated in the MIT Mystery Hunt before? If so, tell us about your Hunt history!', max_length=1500, default='')
    bg_puzzles = models.CharField(verbose_name='Have you played in other puzzle-type events before? If so, feel free to give a short summary.', max_length=1500, default='')
    bg_style = models.CharField(max_length=20, verbose_name='What describes your style of playing?', choices=(('win', 'I’m a puzzle machine and I’d love to be on a team that wants to find the coin. I really want to see the whole hunt.'), ('compete', 'I’m pretty into puzzles, but not so focused on winning'), ('fun', 'I’m just playing for fun, and would like to make some new friends.')), default='fun')
    bg_prefs = models.CharField(verbose_name='Do you have any other preferences about what team you want to join? Would you prefer a bigger or smaller team? Team of current students or of alumni and older players?', max_length=500, default='')
    bg_age = models.CharField(max_length=20, verbose_name='Are you under 18?', choices=(('yes', 'Yes'), ('no', 'No')))
    bg_mit = models.CharField(verbose_name='Are you connected to the MIT community? (If so, how?)', max_length=500, default='')

    other = models.CharField(verbose_name='Anything else you’d like to share with us? Comments, questions, puns?', max_length=1500, null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
