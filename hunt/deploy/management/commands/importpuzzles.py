import os

from django.core.management.base import BaseCommand
from django.conf import settings

from spoilr.core.models import Puzzle, PseudoAnswer, Round, Interaction

from hunt.app.models import RoundData, PuzzleData

from ._common import confirm_command
from ._puzzles import Level, read_puzzles_and_rounds
from ._interactions import read_interactions, import_interactions, import_interactiondatas

class Command(BaseCommand):
    help = 'Re-imports all existing puzzles, rounds, and interactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        inconsistencies, puzzle_info_lookup, round_info_lookup = read_puzzles_and_rounds()
        for inconsistency in inconsistencies:
            print(f'{inconsistency[0]}: {inconsistency[1]}')
        if len(inconsistencies): print()

        has_errors = sum([inconsistency[0] == Level.ERROR for inconsistency in inconsistencies]) > 0
        if has_errors: return

        interaction_infos = read_interactions()
        interaction_urls = set(interaction_info['url'] for interaction_info in interaction_infos)
        unrecognized_interactions = [
            puzzle_info['interaction_to_unlock']
            for puzzle_info in puzzle_info_lookup.values()
            if puzzle_info['interaction_to_unlock'] and puzzle_info['interaction_to_unlock'] not in interaction_urls
        ]
        if len(unrecognized_interactions):
            print('Error: puzzle has unrecognized interactions', unrecognized_interactions)
            return

        if not options['interactive'] or confirm_command():
            # We need to split creating interactions as interactions and puzzles
            # refer to each other.
            interaction_lookup = import_interactions(interaction_infos)
            _import_puzzles(puzzle_info_lookup, round_info_lookup, interaction_lookup)
            import_interactiondatas(interaction_infos, interaction_lookup)

def _import_puzzles(puzzle_info_lookup, round_info_lookup, interaction_lookup):
    PseudoAnswer.objects.all().delete()

    Round.objects.exclude(url__in=round_info_lookup.keys()).delete()
    Puzzle.objects.exclude(external_id__in=puzzle_info_lookup.keys()).delete()

    sample_round_urls = set()
    round_models_lookup = {}
    for round_url, round_info in round_info_lookup.items():
        if round_info['is_sample'] and not settings.HUNT_LOAD_SAMPLE_ROUND:
            print(f'Skipping {round_url} as it is a sample round')
            sample_round_urls.add(round_url)
            continue

        print(f'Importing round {round_url}')
        round, _ = Round.objects.update_or_create(
            url=round_url,
            defaults={
                'name': round_info['name'],
                'order': round_info['order']
            })

        RoundData.objects.update_or_create(round_id=round.id, defaults={})

        round_models_lookup[round.url] = round

    for external_id, puzzle_info in puzzle_info_lookup.items():
        if puzzle_info['round_url'] in sample_round_urls:
            print(f'Skipping {external_id}: {puzzle_info["name"]} as it is a sample puzzle')
            continue

        # Change order for puzzles with the previous order so that we don't run into unique constraints.
        clashing_puzzle = Puzzle.objects.filter(
            round=round_models_lookup[puzzle_info['round_url']],
            order=puzzle_info['order']
        ).exclude(external_id=external_id).first()
        if clashing_puzzle:
            clashing_puzzle.order = -clashing_puzzle.order
            clashing_puzzle.save()

        answer = puzzle_info['answer']
        # alphabetize multianswers
        if ',' in answer:
            answer = ', '.join(sorted(x.strip() for x in answer.split(',')))
        print(f'Importing {external_id}: {puzzle_info["name"]}')
        puzzle, _ = Puzzle.objects.update_or_create(
            external_id=external_id,
            defaults={
                'round': round_models_lookup[puzzle_info['round_url']],
                'url': puzzle_info['url'],
                'name': puzzle_info['name'],
                'answer': answer,
                'credits': puzzle_info['credits'],
                'order': puzzle_info['order'],
                'is_meta': puzzle_info['is_meta']
            })

        puzzledata, _ = PuzzleData.objects.update_or_create(
            puzzle_id=puzzle.id,
            defaults={
                'unlock_order': puzzle_info['unlock_order'],
                'round_solve_count_to_unlock': puzzle_info['round_solve_count_to_unlock'],
                'interaction_to_unlock': (
                    interaction_lookup[puzzle_info['interaction_to_unlock']]
                    if puzzle_info['interaction_to_unlock'] else None)
            }
            # TODO(sahil): Include hints into here too.
        )
        puzzledata.solves_to_unlock.clear()

        if 'pseudo' in puzzle_info:
            for k, v in puzzle_info['pseudo'].items():
                PseudoAnswer(puzzle=puzzle, answer=k, response=v).save()

    # Add feeder puzzle references in a second pass, so we know they've been created.
    for external_id, puzzle_info in puzzle_info_lookup.items():
        if not len(puzzle_info['solves_to_unlock']): continue

        puzzledata = PuzzleData.objects.get(puzzle__external_id=external_id)
        puzzles = Puzzle.objects.filter(external_id__in=puzzle_info['solves_to_unlock'])
        puzzledata.solves_to_unlock.add(*puzzles)
