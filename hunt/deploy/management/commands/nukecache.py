from django.core.management.base import BaseCommand

from hunt.app.core.cache import nuke_cache

from ._common import confirm_command

class Command(BaseCommand):
    help = 'Nukes the hunt cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        if options['interactive'] and not confirm_command('This will nuke the hunt cache'):
            return

        nuke_cache()
