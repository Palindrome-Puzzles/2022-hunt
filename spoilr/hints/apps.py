from django.apps import AppConfig

# Register hunt callbacks.
from . import callbacks

class SpoilrHintsConfig(AppConfig):
    name = 'spoilr.hints'

    # Override the prefix for database model tables.
    label = 'spoilr_hints'
