"""
URL configuration for the 2022 Hunt registration website.
"""

from django.conf import settings
from django.urls import include, path
from .common import common_urlpatterns

urlpatterns = [
    path('', include('hunt.registration.urls')),
]
urlpatterns += common_urlpatterns
