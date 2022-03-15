"""
URL configuration for the 2022 Hunt website.
"""

from django.conf import settings
from django.urls import include, path
from .common import common_urlpatterns

urlpatterns = [
    # Special puzzles - add these first, so they take precedent over standard puzzle
    # URLs.
    path('', include('hunt.data.urls')),
    path('', include('hunt.app.urls')),
    path('hq/', include('spoilr.urls')),
]
urlpatterns += common_urlpatterns

if settings.HUNT_PUZZLEVIEWER_ENABLED:
    urlpatterns += [
        path('puzzlelzzup/', include('hunt.puzzleviewer.urls'))
    ]
