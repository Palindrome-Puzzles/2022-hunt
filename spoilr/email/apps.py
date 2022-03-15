from django.apps import AppConfig

# Register hunt callbacks.
from . import callbacks

class SpoilrEmailConfig(AppConfig):
    name = 'spoilr.email'

    # Override the prefix for database model tables.
    label = 'spoilr_email'
