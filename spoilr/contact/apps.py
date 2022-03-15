from django.apps import AppConfig

from . import callbacks

class SpoilrContactConfig(AppConfig):
    name = 'spoilr.contact'

    # Override the prefix for database model tables.
    label = 'spoilr_contact'
