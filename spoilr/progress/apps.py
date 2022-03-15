from django.apps import AppConfig

class SpoilrProgressConfig(AppConfig):
    name = 'spoilr.progress'

    # Override the prefix for database model tables.
    label = 'spoilr_progress'
