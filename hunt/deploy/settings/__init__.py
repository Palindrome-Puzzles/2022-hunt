import os
from django.core.exceptions import ImproperlyConfigured

def initialize_settings():
    env = os.environ.get('DJANGO_ENV')
    if not env:
        raise ImproperlyConfigured('DJANGO_ENV environment variable is missing')
    if env == 'common':
        raise ImproperlyConfigured('DJANGO_ENV environment variable cannot be "common"')

    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'hunt.deploy.settings.' + env)
