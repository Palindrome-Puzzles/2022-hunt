from django.core.management.base import BaseCommand

from spoilr.core.api.hunt_unsafe import reset_hunt_log
from ._common import confirm_command

class Command(BaseCommand):
    help = 'Resets the hunt system log'

    def handle(self, *args, **options):
        if confirm_command():
            reset_hunt_log()
