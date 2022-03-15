import typing

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

alpha_validator = RegexValidator(r'^[a-zA-Z]*$', 'Only letters are allowed.')

### Section: Hunt solving teams and users.

class TeamType(models.TextChoices):
    # Whether the team is a team controlled by the hunt setters.
    INTERNAL = 'internal', 'Internal Team'

    # Whether the team is for public access.
    PUBLIC = 'public', 'Public Team'

# TODO(sahil): Use Django 4 unique constraint with expressions to make sure usernames are case-insensitive unique.
class Team(models.Model):
    username = models.CharField(max_length=50, unique=True, validators=[alpha_validator])
    name = models.CharField(max_length=200, unique=True)
    rounds = models.ManyToManyField('Round', through='RoundAccess')
    puzzles = models.ManyToManyField('Puzzle', through='PuzzleAccess')
    interactions = models.ManyToManyField('Interaction', through='InteractionAccess')

    type = models.CharField(max_length=20, choices=TeamType.choices, null=True, blank=True)

    @property
    def is_internal(self):
        return self.type == TeamType.INTERNAL

    @property
    def is_public(self):
        return self.type == TeamType.PUBLIC

    @property
    def shared_account(self):
        return self.user_set.filter(team_role=UserTeamRole.SHARED_ACCOUNT).first()

    @property
    def team_email(self):
        return (
            (hasattr(self, 'teamregistrationinfo') and self.teamregistrationinfo.team_email) or
            (self.shared_account and self.shared_account.email))

    # TODO(sahil): Remove this property and work with the request.user.is_staff directly instead.
    @property
    def is_admin(self):
        return self.shared_account.is_staff

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_type_valid",
                check=models.Q(type__in=TeamType.values)
            ),
            models.UniqueConstraint(
                fields=['type'],
                name="%(app_label)s_%(class)s_public_unique",
                condition=models.Q(type=TeamType.PUBLIC)
            )
        ]

class UserTeamRole(models.TextChoices):
    SHARED_ACCOUNT = 'shared', 'Shared Account'
    # Note: In future hunts, we could support each solver having their own
    # user, and it's linked to the team. That could be implemented by adding
    # more roles here, like Captain and Member, along with some team admin
    # pages to browse and add team members.

class User(AbstractUser):
    """
    Custom Django user model to use for the hunt. It includes hunt team related
    metadata.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    team_role = models.CharField(max_length=20, choices=UserTeamRole.choices, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_team_role_valid",
                check=models.Q(team_role__in=UserTeamRole.values),
            ),
            models.UniqueConstraint(
                fields=['team'], condition=models.Q(team_role=UserTeamRole.SHARED_ACCOUNT),
                name='%(app_label)s_%(class)s_unique_team_shared_account'),

            models.CheckConstraint(
                check=models.Q(team__isnull=True, team_role__isnull=True) | models.Q(team__isnull=False, team_role__isnull=False),
                name='%(app_label)s_%(class)s_is_captain_if_team'
            ),
        ]


### Section: Modeling the hunt.

class Round(models.Model):
    url = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']

class Puzzle(models.Model):
    # Deterministic ID for the puzzle, so that code and configuration can reliably
    # refer to a puzzle.
    external_id = models.IntegerField(unique=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    url = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    answer = models.CharField(max_length=100)
    credits = models.TextField(default='')
    order = models.IntegerField()
    is_meta = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        prefix = 'metapuzzle' if self.is_meta else 'puzzle'
        return '%s “%s” (%s)' % (prefix, self.name, self.round)

    @property
    def is_multi_answer(self) -> bool:
        return ',' in self.answer

    @property
    def all_answers(self) -> typing.List[str]:
        return list(sorted(x.strip() for x in self.answer.split(',')))

    class Meta:
        unique_together = ('round', 'order')
        ordering = ['round__order', 'order']

class Interaction(models.Model):
    url = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']

class RoundAccess(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s can see %s' % (self.team, self.round)

    class Meta:
        unique_together = ('team', 'round')
        verbose_name_plural = 'Round access'

class PuzzleAccess(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    solved = models.BooleanField(default=False)
    solved_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        summary = 'can see'
        if self.solved:
            summary = 'has solved'
        return '%s %s %s' % (self.team, summary, self.puzzle)

    class Meta:
        unique_together = ('team', 'puzzle')
        verbose_name_plural = 'Puzzle access'

# Note to future hunt teams.
# This model is badly named. Interactions model that HQ needs to take some action,
# so "access" (implying the solvers have access to the interaction) is the wrong
# metaphor. Maybe something like `TeamInteraction` is a better name?
class InteractionAccess(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    accomplished = models.BooleanField(default=False)
    accomplished_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        summary = 'can accomplish'
        if self.accomplished:
            summary = 'has accomplished'
        return '%s %s %s' % (self.team, summary, self.interaction)

    class Meta:
        unique_together = ('team', 'interaction')
        verbose_name_plural = 'Interaction access'


### Section: Extra puzzle behavior.

class Minipuzzle(models.Model):
    """
    The model for a team's progress on minipuzzles within a puzzle.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    ref = models.CharField(max_length=128)
    solved = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)
    solved_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['team', 'puzzle', 'ref']]

class PseudoAnswer(models.Model):
    """
    Possible answers a solver might input that don't mark the puzzle as correct,
    but need handling.

    For example, they might provide a nudge for teams that are on the right
    track, or special instructions for how to obtain the correct answer.
    """
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    response = models.TextField()

    def __str__(self):
        return '"%s" (%s)' % (self.puzzle.name, self.answer)

    class Meta:
        unique_together = ('puzzle', 'answer')
        ordering = ['puzzle', 'answer']


### Section: Puzzle and minipuzzle submission.

class PuzzleSubmission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    raw_answer = models.TextField()
    answer = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return '%s: %s submitted for %s' % (self.timestamp, self.team, self.puzzle)

    class Meta:
        unique_together = ('team', 'puzzle', 'answer')
        ordering = ['-timestamp']

class MinipuzzleSubmission(models.Model):
    minipuzzle = models.ForeignKey(Minipuzzle, on_delete=models.CASCADE, related_name='submissions')
    raw_answer = models.TextField()
    answer = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('minipuzzle', 'answer')
        ordering = ['-create_time']


### Section: Hunt glue models.

class HuntSetting(models.Model):
    """
    Settings that describe the hunt's current state.

    This is a shared repository for spoilr and hunt-specific code, so be careful
    to namespace settings to avoid collisions.
    """
    name = models.CharField(max_length=200, unique=True)

    # Only one of the following fields should be set.
    text_value = models.TextField(null=True, blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    date_value = models.DateTimeField(null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Setting {self.name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(text_value__isnull=False, boolean_value__isnull=True, date_value__isnull=True) |
                    models.Q(text_value__isnull=True, boolean_value__isnull=False, date_value__isnull=True) |
                    models.Q(text_value__isnull=True, boolean_value__isnull=True, date_value__isnull=False) |
                    models.Q(text_value__isnull=True, boolean_value__isnull=True, date_value__isnull=True)
                ),
                name='%(app_label)s_%(class)s_one_value'
            ),
        ]

class SystemLog(models.Model):
    """Audit log for any changes to the hunt state."""
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        prefix = f'[{self.team}] ' if self.team else ''
        return f'{prefix} {self.timestamp}: {self.message}'

    class Meta:
        verbose_name_plural = "System log"

# TODO(sahil): Rewrite updates - could use a better model, and move it to its own spoilr app.
class HQUpdate(models.Model):
    """
    Represent a message from headquarters to all teams. Shows up on an "updates" page as well as going out by
    email
    """

    subject = models.CharField(max_length=200)
    body = models.TextField()
    published = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(blank=True, auto_now=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    puzzle = models.ForeignKey(Puzzle, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Errata for Puzzle')
    send_email = models.BooleanField(default=True)

    def __str__(self):
        return '%s' % (self.subject)
