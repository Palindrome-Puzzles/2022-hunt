import logging

from django import template
from django.template import Template, Context

from hunt.app.core.interactions import get_submission_instructions
from hunt.app.views.common import get_puzzle_context
from hunt.data_loader.puzzle import get_puzzle_data_text

from spoilr.core.models import InteractionAccess

logger = logging.getLogger(__name__)
register = template.Library()

@register.simple_tag
def self_help_submission(puzzle, team):
    maybe_interactiondata = puzzle.interactiondata_set.select_related('interaction').first()
    maybe_interaction = maybe_interactiondata.interaction if maybe_interactiondata else None
    if maybe_interaction:
        puzzle_context = get_puzzle_context(team, puzzle)
        message = get_puzzle_data_text(puzzle.url, 'message.tmpl')
        interaction_access = InteractionAccess.objects.filter(interaction=maybe_interaction, team=team).first()
        return {
            'message': Template(message).render(Context(puzzle_context)),
            'interaction': maybe_interaction,
            'interaction_access': interaction_access,
            'instructions': get_submission_instructions(maybe_interaction, team,
                                                        has_submitted=bool(interaction_access)),
        }
    logger.error(f'Should have been able to show a self-help submission for {puzzle} to {team}')
    return {}
