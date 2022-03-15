from django.urls import re_path

from .core.notifications import TeamNotificationsConsumer

websocket_urlpatterns = [
    # One-way broadcast socket for team notifications for things such as puzzle
    # unlocks or HQ updates.
    re_path('^ws/team$', TeamNotificationsConsumer.as_asgi()),
]
