from django.core.management.base import BaseCommand

from ._puzzles import read_puzzles_and_rounds

class Command(BaseCommand):
    help = 'Audits the puzzle list and assets to find inconsistencies'

    def handle(self, *args, **options):
        inconsistencies, _, _ = read_puzzles_and_rounds()
        for inconsistency in inconsistencies:
            print(f'{inconsistency[0]}: {inconsistency[1]}')
