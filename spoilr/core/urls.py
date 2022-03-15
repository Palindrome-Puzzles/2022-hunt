from django.urls import path, re_path, include
from django.conf import settings

from spoilr.core.views import hunt_views
from spoilr.core.views import shortcut_views
from spoilr.core.views import team_views

# HQ and hunt management.
urlpatterns = [
    # Impersonating teams.
    re_path('^impersonate/(?P<team_username>.*)/?$', team_views.impersonate_view, name='impersonate'),
    path('end-impersonate/', team_views.end_impersonate_view, name='end_impersonate'),

    # Shortcuts to change the state of a puzzle.
    path('shortcuts/', shortcut_views.shortcuts_view, name='shortcuts'),

    # Global tick. Refresh this page regularly to trigger time-based events such as
    # unlocking puzzles.
    path('tick/', hunt_views.tick_view, name='tick'),
]

if settings.SPOILR_ENABLE_DJANGO_ADMIN:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

if settings.SPOILR_ENABLE_DJANGO_ADMIN and settings.SPOILR_ENABLE_DJANGO_ADMIN_DOCS:
    urlpatterns += [
        path('admin/docs/', include('django.contrib.admindocs.urls')),
    ]
