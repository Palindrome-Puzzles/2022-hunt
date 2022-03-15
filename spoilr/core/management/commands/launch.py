from django.core.management.base import BaseCommand

from spoilr.core.api.hunt import launch_site

class Command(BaseCommand):
    help = 'Launches a hunt site, or the hunt itself'

    def add_arguments(self, parser):
        parser.add_argument(
            'site', type=str,
            help="The reference of the site to launch, or 'hunt' to make the hunt available to solvers.",
        )

    def handle(self, *args, **options):
        launch_site(options['site'])
