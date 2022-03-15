from django.apps import AppConfig

class HuntRegistrationConfig(AppConfig):
    name = 'hunt.registration'

    # Override the prefix for database model tables.
    label = 'hunt_registration'
