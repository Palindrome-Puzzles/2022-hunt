import datetime

from django_hosts.resolvers import reverse as hosts_reverse
from django.conf import settings

from hunt.app.core.rewards import get_bonus_content
from hunt.app.core.constants import ROUND_RD3_URLS, ROUND_ENDGAME_URL
from spoilr.core.api.events import HuntEvent, register, register_wildcard, HandlerPriority

# Note: imports are lazily performed within each callback to avoid importing
# models before the app is ready.

def send_to_discord(event_type, message, team, **kwargs):
    # TODO(sahil): Dispatch the message to Discord.
    pass

def notify_team(event_type, team, round=None, puzzle=None, interaction=None, **kwargs):
    from .assets.refs import get_round_static_path
    from .notifications import notify_team_log
    from .rewards import get_reward_info
    from hunt.app.models import InteractionType

    if not team or team.is_public:
        return

    if event_type in (HuntEvent.PUZZLE_RELEASED, HuntEvent.METAPUZZLE_RELEASED):
        notify_team_log(
            team=team, event_type=event_type, message=f'<em>Unlocked puzzle</em> {puzzle.name} ({puzzle.round.name})',
            theme='puzzle_released',
            link=hosts_reverse('puzzle_view', args=(puzzle.url,), host='site-1'))

    elif event_type in (HuntEvent.PUZZLE_SOLVED, HuntEvent.METAPUZZLE_SOLVED):
        notify_team_log(
            team=team, event_type=event_type, message=f'<em>Solved puzzle</em> {puzzle.name} ({puzzle.round.name})',
            theme='puzzle_solved',
            link=hosts_reverse('puzzle_view', args=(puzzle.url,), host='site-1'),
            puzzle_url=puzzle.url,
            sound_url=get_round_static_path(puzzle.round.url, variant='round') + 'answer.mp3',
            reward_info=get_reward_info(event_type, puzzle, team),
            bonus_content=get_bonus_content(puzzle, team))

    elif event_type == HuntEvent.ROUND_RELEASED:
        if (round.url == 'endgame'):
            return
        notify_team_log(
            team=team, event_type=event_type, message=f'<em>Round unlocked</em> {round.name}',
            theme='round_released',
            link=hosts_reverse('round_view', args=(round.url,), host='site-1'))

    elif event_type == HuntEvent.INTERACTION_RELEASED and interaction.interactiondata.type == InteractionType.SUBMISSION:
        puzzle = interaction.interactiondata.puzzle_trigger
        if puzzle:
            notify_team_log(
                team=team, event_type=event_type,
                theme='task_sent',
                message=f'<em>Task sent</em> {interaction}',
                link=hosts_reverse('puzzle_view', args=(puzzle.url,), host='site-1'))

    elif event_type == HuntEvent.INTERACTION_ACCOMPLISHED and interaction.interactiondata.type == InteractionType.SUBMISSION:
        puzzle = interaction.interactiondata.puzzle_trigger
        if puzzle:
            notify_team_log(
                team=team, event_type=event_type,
                theme='task_done',
                message=f'<em>Task complete</em> {interaction}',
                link=hosts_reverse('puzzle_view', args=(puzzle.url,), host='site-1'))

    elif event_type in (HuntEvent.INTERACTION_RELEASED, HuntEvent.INTERACTION_REOPENED) and interaction.interactiondata.type == InteractionType.ANSWER:
        notify_team_log(
            team=team, event_type=event_type,
            theme='task_sent',
            message=f'<em>Manuscrip request sent</em> {interaction}',
            link=hosts_reverse('rewards_drawer', host='site-1'))

    # TODO(sahil): Add others team notification like hints being resolved?

def clear_caches(event_type, team, round=None, puzzle=None, interaction=None, **kwargs):
    from .cache import team_puzzle_updated, team_updated, team_round_updated, nuke_page_category, nuke_cache, TEAMS_LIST_CATEGORY

    if event_type in (
        HuntEvent.PUZZLE_ATTEMPTED, HuntEvent.PUZZLE_INCORRECTLY_ATTEMPTED,
        HuntEvent.METAPUZZLE_ATTEMPTED, HuntEvent.METAPUZZLE_INCORRECTLY_ATTEMPTED,
        HuntEvent.MINIPUZZLE_ATTEMPTED, HuntEvent.MINIPUZZLE_COMPLETED,
        HuntEvent.HINT_REQUESTED, HuntEvent.HINT_RESOLVED
    ):
        team_puzzle_updated(team, puzzle)

    if event_type in (
        HuntEvent.PUZZLE_RELEASED, HuntEvent.METAPUZZLE_RELEASED,
        HuntEvent.HUNT_PUZZLE_SHORTCUT
    ):
        team_round_updated(team, puzzle.round)

    if event_type in (
        HuntEvent.PUZZLE_SOLVED, HuntEvent.METAPUZZLE_SOLVED,
        # TODO(sahil): See if we can tighten the cache-breaking for interactions.
        HuntEvent.INTERACTION_RELEASED, HuntEvent.INTERACTION_ACCOMPLISHED, HuntEvent.INTERACTION_REOPENED,
        HuntEvent.ROUND_RELEASED, HuntEvent.TEAM_UPDATED
    ):
        team_updated(team)

    if event_type in (HuntEvent.HUNT_SITE_LAUNCHED, HuntEvent.HUNT_ACTIVITY_RESET, HuntEvent.UPDATE_SENT):
        nuke_cache()

    # Used in registration site.
    if event_type in (HuntEvent.TEAM_REGISTERED, HuntEvent.TEAM_UPDATED):
        nuke_page_category(TEAMS_LIST_CATEGORY)

def on_hunt_site_launched(site_ref, **kwargs):
    from hunt.deploy.util import HUNT_REF, HUNT_RD0_REF, HUNT_PRELAUNCH_REF

    from .puzzles import unlock_available_puzzles
    from .notifications import notify_hunt_launched

    unlock_available_puzzles()

    if site_ref == HUNT_REF:
        notify_hunt_launched()

def on_progressed(team, puzzle=None, **kwargs):
    from .puzzles import unlock_available_puzzles
    from .interactions import unlock_puzzle_interactions

    if team:
        unlock_available_puzzles(team)
    if team and puzzle:
        unlock_puzzle_interactions(team, puzzle)

def on_team_registered(team, **kwargs):
    from .puzzles import unlock_available_puzzles

    unlock_available_puzzles(team)

def update_hints_release_delay(puzzle, **kwargs):
    from spoilr.core.models import PuzzleAccess, TeamType

    if puzzle.puzzledata.hints_release_delay:
        return

    is_act3_or_act4 = puzzle.round.url in ROUND_RD3_URLS or puzzle.round.url == ROUND_ENDGAME_URL
    solves_before_hints = (
        settings.HUNT_RD3_SOLVES_BEFORE_HINTS_RELEASED
        if is_act3_or_act4
        else settings.HUNT_SOLVES_BEFORE_HINTS_RELEASED)

    solves = PuzzleAccess.objects.exclude(team__type=TeamType.INTERNAL).filter(puzzle=puzzle, solved=True).order_by('solved_time')
    first_n_solves = solves[:solves_before_hints]

    if len(first_n_solves) >= solves_before_hints:
        total_stuck_time = datetime.timedelta(seconds=0)
        for solve in first_n_solves:
            total_stuck_time += solve.solved_time - solve.timestamp
        average_stuck_time = total_stuck_time / len(first_n_solves)

        puzzle.puzzledata.hints_release_delay = average_stuck_time
        puzzle.puzzledata.save()

def on_email_received(incoming_message, **kwargs):
    from .interactions import unlock_email_interactions

    unlock_email_interactions(incoming_message)

def on_hq_update(update, **kwargs):
    from .notifications import notify_hq_update

    notify_hq_update(update)

register_wildcard(send_to_discord)
register_wildcard(notify_team)
register_wildcard(clear_caches)

register(HuntEvent.HUNT_SITE_LAUNCHED, on_hunt_site_launched)
register(HuntEvent.TEAM_REGISTERED, on_team_registered)
register(HuntEvent.PUZZLE_SOLVED, on_progressed)
register(HuntEvent.METAPUZZLE_SOLVED, on_progressed)
register(HuntEvent.INTERACTION_ACCOMPLISHED, on_progressed)
register(HuntEvent.PUZZLE_SOLVED, update_hints_release_delay)
register(HuntEvent.METAPUZZLE_SOLVED, update_hints_release_delay)
register(HuntEvent.EMAIL_RECEIVED, on_email_received, priority=HandlerPriority.HIGH)
register(HuntEvent.UPDATE_SENT, on_hq_update)

# TODO(sahil): Add events that interact with queuebot.
# TODO(sahil): Add event for HQ updates.
