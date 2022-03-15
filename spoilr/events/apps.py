from django.apps import AppConfig

class SpoilrEventsConfig(AppConfig):
    name = 'spoilr.events'

    # Override the prefix for database model tables.
    label = 'spoilr_events'
