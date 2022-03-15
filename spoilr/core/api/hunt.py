"""Business logic for querying or updating the hunt state."""
import logging

from django.utils.timezone import now

from spoilr.core.models import RoundAccess, PuzzleAccess, InteractionAccess, HuntSetting

from .cache import memoized_cache, clear_memoized_cache
from .events import dispatch, HuntEvent

logger = logging.getLogger(__name__)

SITE_LAUNCH_TIME_CACHE_BUCKET = 'site_launch_time'

@memoized_cache(SITE_LAUNCH_TIME_CACHE_BUCKET)
def get_site_launch_time(site_ref):
    setting, _ = HuntSetting.objects.get_or_create(name=f'spoilr.{site_ref}.launch_time')
    return setting.date_value

def is_site_launched(site_ref):
    site_launch_time = get_site_launch_time(site_ref)
    return site_launch_time and site_launch_time <= now()

@clear_memoized_cache(SITE_LAUNCH_TIME_CACHE_BUCKET)
def launch_site(site_ref):
    setting, _ = HuntSetting.objects.get_or_create(name=f'spoilr.{site_ref}.launch_time')
    if not setting.date_value:
        setting.date_value = now()
        setting.save()
    dispatch(
        HuntEvent.HUNT_SITE_LAUNCHED, site_ref=site_ref,
        message=f'Launched site {site_ref} at {setting.date_value}')

def release_round(team, round):
    """Release a round to a team."""
    round_access, created = RoundAccess.objects.get_or_create(team=team, round=round)
    if created:
        logger.info("released %s/round/%s", team.username, round.url)
        dispatch(
            HuntEvent.ROUND_RELEASED, team=team, round=round, object_id=round.url,
            round_access=round_access,
            message=f'Released round "{round}"')
    return round_access

def release_rounds(team, rounds):
    """Release many rounds to a team."""
    _release_many(team, rounds, 'round', RoundAccess, HuntEvent.ROUND_RELEASED)

def release_puzzle(team, puzzle):
    """Release a puzzle to a team."""
    puzzle_access, created = PuzzleAccess.objects.get_or_create(team=team, puzzle=puzzle)
    if created:
        logger.info("released %s/puzzle/%s", team.username, puzzle.url)
        dispatch(
            HuntEvent.METAPUZZLE_RELEASED if puzzle.is_meta else HuntEvent.PUZZLE_RELEASED,
            team=team, puzzle=puzzle, puzzle_access=puzzle_access, object_id=puzzle.url,
            message=f'Released {puzzle}')
    return puzzle_access

def release_puzzles(team, puzzles):
    """Release many puzzles to a team."""
    _release_many(team, puzzles, 'puzzle', PuzzleAccess, HuntEvent.PUZZLE_RELEASED)

def release_interaction(team, interaction, *, reopen=False):
    """Release an interaction to a team."""
    interaction_access, created = InteractionAccess.objects.get_or_create(team=team, interaction=interaction)
    if created:
        logger.info("released %s/interaction/%s", team.username, interaction.url)
        dispatch(
            HuntEvent.INTERACTION_RELEASED, team=team, interaction=interaction,
            interaction_access=interaction_access, object_id=interaction.url,
            message=f'Released interaction "{interaction}"')
    elif not created and reopen:
        interaction_access.accomplished = False
        interaction_access.accomplished_time = None
        interaction_access.save()
        logger.info("reopened %s/interaction/%s", team.username, interaction.url)
        dispatch(
            HuntEvent.INTERACTION_REOPENED, team=team, interaction=interaction,
            interaction_access=interaction_access, object_id=interaction.url,
            message=f'Reopened interaction "{interaction}"')
    return interaction_access

def release_interactions(team, interactions):
    """Release many interactions to a team."""
    _release_many(team, interactions, 'interaction', InteractionAccess, HuntEvent.INTERACTION_RELEASED)

def accomplish_interaction(*, interaction_access=None, team=None, interaction=None):
    """Mark an interaction as completed by a team."""
    if not interaction_access:
        assert team and interaction
        interaction_access = InteractionAccess.objects.get(team=team, interaction=interaction)
    team = interaction_access.team
    interaction = interaction_access.interaction

    if interaction_access.accomplished:
        return

    interaction_access.accomplished = True
    interaction_access.accomplished_time = now()
    interaction_access.save()

    logger.info("accomplished interaction %s/interaction/%s", team.username, interaction.url)
    dispatch(
        HuntEvent.INTERACTION_ACCOMPLISHED, team=team, interaction=interaction,
        interaction_access=interaction_access, object_id=interaction.url,
        message=f'Accomplished interaction "{interaction}"')

def _release_many(team, models, model_name, AccessModel, event_type):
    existing_ids = set([
        getattr(access, f'{model_name}_id')
        for access in AccessModel.objects.filter(team=team, **{f'{model_name}__in': models})
    ])

    missing_accesses = [
        AccessModel(team=team, **{model_name: model})
        for model in models
        if model.id not in existing_ids
    ]
    AccessModel.objects.bulk_create(missing_accesses)

    for access in missing_accesses:
        model = getattr(access, model_name)
        logger.info(f'released {team.username}/{model_name}/{model.url}')
        dispatch(
            event_type, team=team, **{model_name: model, f'{model_name}_access': access},
            object_id=model.url,
            message=f'Released {model_name} "{model}"')
