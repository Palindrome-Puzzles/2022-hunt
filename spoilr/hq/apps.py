from django.apps import AppConfig

# Register hunt callbacks.
from . import callbacks

class SpoilrHqConfig(AppConfig):
    name = 'spoilr.hq'

    # Override the prefix for database model tables.
    label = 'spoilr_hq'
