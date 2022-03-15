import logging, re, urllib.parse

from django.conf import settings
from django.shortcuts import reverse
from django.utils.http import urlencode

from hunt.app.models import InteractionType
from hunt.deploy.util import is_autopilot
from spoilr.core.models import Interaction, Team, PuzzleAccess
from spoilr.core.api.hunt import release_interaction, release_interactions, accomplish_interaction

logger = logging.getLogger(__name__)

RE_SUBMISSIONS_SUBJECT = re.compile(r'''^([^\s]+|Book Reports) (for|from) (.+)$''', re.IGNORECASE)

def unlock_puzzle_interactions(team, puzzle):
    """
    Unlock interactions that are available for the team after solving the specified puzzle.

    If it has both a puzzle trigger and an email trigger, then do nothing for now.
    """
    for interaction in Interaction.objects.filter(interactiondata__puzzle_trigger=puzzle, interactiondata__email_key_trigger__isnull=True).exclude(interactionaccess__team=team):
        access = release_interaction(team, interaction)
        if is_autopilot():
            accomplish_interaction(interaction_access=access)

# TODO(sahil): Notify Discord too when we have exceptions here.
def unlock_email_interactions(incoming_message):
    interaction = None
    team = None

    subject = incoming_message.subject

    # TODO(sahil): Sometimes messages have multiple emails in the to field, such
    # as `submissions@mitmh2022.com,my-group@googlegroups.com`. And sometimes
    # they have a name and email such as `Submissions <submissions@mitmh2022.com>`.
    # We use stripped_recipient for the second case, and substring checks for the
    # first case. But if both happen at once, this will be weirdly broken. Consider
    # strategies for dealing with it?

    if settings.HUNT_SUBMISSIONS_EMAIL and settings.HUNT_SUBMISSIONS_EMAIL.lower() in incoming_message.stripped_recipient.lower():
        match = RE_SUBMISSIONS_SUBJECT.search(subject)
        if not match:
            logger.error(f'Unrecognized submission subject {subject}')
            return

        interaction_key, team_key = match.group(1), match.group(3)
        interaction = Interaction.objects.filter(
            interactiondata__email_key_trigger__iexact=interaction_key
            ).first()
        team = Team.objects.filter(username__iexact=team_key).first()

    if settings.BOOK_REPORTS_EMAIL and settings.BOOK_REPORTS_EMAIL.lower() in incoming_message.stripped_recipient.lower():
        interaction = Interaction.objects.filter(
            url__iexact="book-reports"
            ).first()

        match = RE_SUBMISSIONS_SUBJECT.search(subject)
        if match:
            team_key = match.group(3)
            team = Team.objects.filter(name__iexact=team_key).first()

    if settings.EMOJI_ART_EMAIL and settings.EMOJI_ART_EMAIL.lower() in incoming_message.stripped_recipient.lower():
        interaction = Interaction.objects.filter(
            url__iexact="emoji-art"
            ).first()

        match = RE_SUBMISSIONS_SUBJECT.search(subject)
        if match:
            team_key = match.group(3)
            team = Team.objects.filter(name__iexact=team_key).first()

    if interaction or team:
        incoming_message.interaction = interaction
        incoming_message.team = team
        incoming_message.save()

    if not interaction or not team:
        logger.error(f'Couldn\'t decipher team or interaction in {subject}')
        return

    if not on_interaction_email_received(interaction, team):
        # For some reason, we couldn't release an interaction so clear the
        # interaction field.
        incoming_message.interaction = None
        incoming_message.save()

def on_interaction_email_received(interaction, team):
    should_release = not interaction.interactiondata.puzzle_trigger

    if interaction.interactiondata.puzzle_trigger:
        puzzle_access = PuzzleAccess.objects.filter(puzzle=interaction.interactiondata.puzzle_trigger, team=team)
        if interaction.interactiondata.puzzle_trigger_solved:
            should_release = puzzle_access.filter(solved=True).exists()
        else:
            should_release = puzzle_access.exists()

    if should_release:
        release_interaction(team, interaction)
        return True
    else:
        subject = get_email_interaction_subject(interaction, team)
        logger.error(f'Did not release interaction for {subject} as team does not have enough access to puzzle {interaction.interactiondata.puzzle_trigger}')
        return False

def get_email_interaction_subject(interaction, team):
    return f"{interaction.interactiondata.email_key_trigger} for {team.username}"

def get_submission_instructions(interaction, maybe_team, has_submitted):
    if not maybe_team or maybe_team.is_public:
        return 'During the hunt, teams emailed their submissions to HQ to make progress on the meta.'

    if is_autopilot():
        prefix = '<p><strong>When the hunt was active, we asked teams to email their submissions for review. You\'re welcome to still send us a submission for this task if you want, but it\'s no longer required. This puzzle is complete.</strong> Submissions should be sent to'
    else:
        prefix = 'Submissions should be sent to'
    return f'{prefix} {get_email_submission_instructions(interaction, maybe_team, has_submitted)}.'

def get_email_submission_instructions(interaction, team, has_submitted):
    if settings.HUNT_SUBMISSIONS_EMAIL:
        to = settings.HUNT_SUBMISSIONS_EMAIL
        subject = get_email_interaction_subject(interaction, team)
        return f'<a href="mailto:{to}?subject={urllib.parse.quote(subject)}" target="_blank">{to}</a> with the subject “{subject}”'

    elif team.is_admin and not has_submitted:
        return f'<a href="{ reverse("magic_release_interaction", args=(interaction.url,)) }">[simulate emailing]</a>'

    else:
        return '[email simulated already]'
