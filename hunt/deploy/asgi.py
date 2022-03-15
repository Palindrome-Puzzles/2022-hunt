"""
ASGI config for the 2022 Hunt Server project.

It exposes the ASGI callable as a module-level variable named `application`.
The application is wrapped with Channels middleware to power async features
such as WebSockets.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""
# First initialize settings and setup Django models before fetching any other hunt code.
import django
from hunt.deploy.settings import initialize_settings

initialize_settings()
django.setup()

import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application, ProtocolTypeRouter, URLRouter
from django.conf import settings

import hunt.app.routing
import hunt.data.routing

logging.basicConfig(level=settings.ROOT_LOG_LEVEL)

application = ProtocolTypeRouter({
    # Channels handles HTTP automatically, so no need to specify.

    # AuthMiddlewareStack enables standard Django authentication for these URLs.
    # See https://channels.readthedocs.io/en/latest/topics/authentication.html.
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # Puzzle-specific routes - add these first for precedence.
            hunt.data.routing.websocket_urlpatterns +
            hunt.app.routing.websocket_urlpatterns
        )
    ),
})

