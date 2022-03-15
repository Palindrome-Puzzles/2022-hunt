"""
WSGI config for 2022 Hunt Server project.

It exposes the WSGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import logging

from django.conf import settings
from django.core.wsgi import get_wsgi_application

from hunt.deploy.settings import initialize_settings

initialize_settings()

logging.basicConfig(level=settings.ROOT_LOG_LEVEL)

application = get_wsgi_application()
