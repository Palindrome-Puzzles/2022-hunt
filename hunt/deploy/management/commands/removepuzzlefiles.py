import os.path, shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from ._common import confirm_command

class Command(BaseCommand):
    help = 'Removes all puzzle and round files from the static temp directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        if options['interactive'] and not confirm_command('This will delete all files from the static temp directory!'):
            return

        _remove_static_temp()

def _remove_static_temp():
    if os.path.exists(settings.HUNT_ASSETS_TEMP_FOLDER):
        shutil.rmtree(settings.HUNT_ASSETS_TEMP_FOLDER)
