from django.db import models
from spoilr.core.models import Puzzle, Round, Team, Interaction, InteractionAccess
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import math
import json

class TeamData(models.Model):
    """Hunt-specific data for teams."""
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    auth = models.CharField(max_length=128)

    missing_documents = models.BooleanField(default=False)
    extra_puzzle_radius = models.SmallIntegerField(default=0)

    act2_puzzle_radius_increased = models.BooleanField(default=False)
    radius_increased_1 = models.BooleanField(default=False)

    act3_release = models.BooleanField(default=False)
    act3_release_emailed = models.BooleanField(default=False)
    act3_release_1 = models.BooleanField(default=False)
    act3_release_1_emailed = models.BooleanField(default=False)
    act3_release_2 = models.BooleanField(default=False)
    act3_release_2_emailed = models.BooleanField(default=False)
    act3_release_3_emailed = models.BooleanField(default=False)

    def __str__(self):
        return u'%s' % (self.team.name)

    class Meta:
        verbose_name = 'Team data'
        verbose_name_plural = 'Team data'

class PuzzleData(models.Model):
    """Hunt-specific data for puzzles."""
    puzzle = models.OneToOneField(Puzzle, on_delete=models.CASCADE)
    unlock_order = models.IntegerField(null=True, blank=True)
    round_solve_count_to_unlock = models.IntegerField(null=True, blank=True)
    solves_to_unlock = models.ManyToManyField(Puzzle, related_name='+')
    interaction_to_unlock = models.ForeignKey(Interaction, null=True, blank=True, on_delete=models.SET_NULL)

    # Whether hints have been released for this puzzle manually, as it was
    # deemed too hard.
    hints_force_released = models.BooleanField(default=False)
    # How long until we release hints for this puzzle. This is automatically
    # calculated as the puzzle is solved.
    hints_release_delay = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.puzzle.name

    class Meta:
        verbose_name = 'Puzzle data'
        verbose_name_plural = 'Puzzle data'

class RoundData(models.Model):
    """Hunt-specific data for rounds."""
    round = models.OneToOneField(Round, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Round data'
        verbose_name_plural = 'Round data'

class InteractionType(models.TextChoices):
    # The team is submitting extra content for a puzzle. HQ needs to grade the
    # content and respond if needed.
    # This interaction is automatically created when the team sends us an email with a
    # specific subject, with the interaction's `email_key` field.
    SUBMISSION = 'submission', 'Submission for puzzle'

    # The team has unlocked a story interaction. HQ needs to schedule a live
    # interaction, or send a fallback email with the interaction content.
    # This interaction is automatically created either when the team solves the
    # puzzle in the `puzzle` field.
    STORY = 'story', 'Story'

    # The team has become eligible for automatically unlocking some hunt content.
    # HQ needs to approve giving the team access, and send an email to the
    # captain with an unlock link.
    UNLOCK = 'unlock', 'Unlock'

    # The team has requested a free answer ("spending a Manuscrip") for a puzzle.
    # HQ needs to contact the captain and get them to approve spending the free
    # answer token.
    ANSWER = 'answer', 'Answer'

class InteractionData(models.Model):
    """Hunt-specific data for interactions."""
    interaction = models.OneToOneField(Interaction, on_delete=models.CASCADE)
    type = models.CharField(max_length=64, choices=InteractionType.choices)

    # The template to use for a meeting invite sent in response to an interaction.
    invite_template = models.TextField(null=True, blank=True)
    # The template to use for an email sent in response to an interaction.
    message_template = models.TextField(null=True, blank=True)

    # The puzzle which when solved automatically unlocks this interaction.
    puzzle_trigger = models.ForeignKey(Puzzle, blank=True, null=True, on_delete=models.SET_NULL)
    # Whether the puzzle needs to be solved (True) or unlocked (False) before this
    # interaction is available.
    puzzle_trigger_solved = models.BooleanField(blank=True, null=True)
    # The email key, which when in the subject on an email, will automatically
    # create or unsnooze this interaction. If there is also a puzzle trigger,
    # then the relevant puzzle also needs to be solved/unlocked (depending on
    # `puzzle_trigger_solved`).
    email_key_trigger = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_type_valid",
                check=models.Q(type__in=InteractionType.values),
            ),
        ]

class TeamSession(models.Model):
    """
    Generic session information for a group of users within a team.

    Group types are a general way to describe how to group users within a team.
    For example, one group type could be used for collaboration on a specific
    puzzle, and another group type could be used for notifications sent to the
    entire team. It's up to the application layer to ensure each group of users
    receives a unique and deterministic group type.

    A team can have at most one session with a given group type. This session
    object gets reused every time team members access that group type.

    Unstructured JSON data can be stored as part of the team session. If this
    isn't sufficient, puzzles can define their own models for storing more data,
    and should include a one-to-one link to the team session.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    group_type = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)
    data = models.JSONField()

    class Meta:
        unique_together = ('team', 'group_type')

class FreeUnlockStatus(models.TextChoices):
    NEW = 'new', 'New request'
    APPROVED = 'approved', 'Approved request'
    CANCELLED = 'cancelled', 'Cancelled request'
    WITHDRAWN = 'withdrawn', 'Withdrew request'

class FreeUnlockRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="free_unlocks")
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=FreeUnlockStatus.choices, default=FreeUnlockStatus.NEW)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'puzzle')
