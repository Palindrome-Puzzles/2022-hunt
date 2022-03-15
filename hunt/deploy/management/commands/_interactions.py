import csv

from spoilr.core.models import Interaction, Puzzle
from hunt.app.models import InteractionData, InteractionType

from hunt.data_loader.hunt_info import get_hunt_info

from ._common import INTERACTIONS_LIST_PATH, row_get, row_get_int, row_get_yesno

def import_interactions(interaction_infos):
    'Updates interactions from interactions.tsv in-place'
    interaction_urls = set(interaction_info['url'] for interaction_info in interaction_infos)
    Interaction.objects.exclude(url__in=interaction_urls).delete()

    interaction_lookup = {}
    for interaction_info in interaction_infos:
        print(f'Importing {interaction_info["url"]}')

        # Change order for interactions with the previous order so that we don't run into unique constraints.
        clashing_interaction = Interaction.objects.filter(
            order=interaction_info['order']
        ).exclude(url=interaction_info['url']).first()
        if clashing_interaction:
            clashing_interaction.order = -clashing_interaction.order
            clashing_interaction.save()

        interaction, _ = Interaction.objects.update_or_create(
            url=interaction_info['url'],
            defaults={
                'name': interaction_info['name'],
                'order': interaction_info['order'],
            })
        interaction_lookup[interaction_info['url']] = interaction
    return interaction_lookup

def import_interactiondatas(interaction_infos, interaction_lookup):
    'Updates interaction data from interactions.tsv in-place'

    for interaction_info in interaction_infos:
        print(f'Importing data for {interaction_info["url"]}')

        interaction = interaction_lookup[interaction_info['url']]

        puzzle_trigger = (
            Puzzle.objects.get(external_id=interaction_info['puzzle_trigger'])
            if interaction_info['puzzle_trigger'] else None)

        InteractionData.objects.update_or_create(
            interaction=interaction,
            defaults={
                'type': interaction_info['type'],
                'puzzle_trigger': puzzle_trigger,
                'puzzle_trigger_solved': interaction_info['puzzle_trigger_solved'],
                'email_key_trigger': interaction_info['email_key_trigger'],
                'invite_template': interaction_info['invite_template'],
                'message_template': interaction_info['message_template'],
            })

def read_interactions():
    interactions = []
    with open(get_hunt_info(INTERACTIONS_LIST_PATH), encoding='utf-8') as f:
        # Open interaction list and skip header row.
        reader = csv.reader(f, delimiter='\t')
        next(reader)

        for row in reader:
            if len(row) == 0: continue

            interaction = {}
            interaction['url'] = row_get(row, 0)
            interaction['name'] = row_get(row, 1)
            interaction['order'] = row_get_int(row, 2)
            interaction['type'] = row_get(row, 3)
            interaction['puzzle_trigger'] = row_get_int(row, 4, None)
            interaction['puzzle_trigger_solved'] = row_get_yesno(row, 5)
            interaction['email_key_trigger'] = row_get(row, 6, None)
            interaction['invite_template'] = row_get(row, 7, None)
            interaction['message_template'] = row_get(row, 8, None)

            if not interaction['url'] or not interaction['name'] or not interaction['order'] or not interaction['type']:
                raise CommandError('interaction is missing required fields, cannot proceed')
            else:
                interactions.append(interaction)
    return interactions

def _valid_url(username):
    # TODO(sahil): Implement
    return True

