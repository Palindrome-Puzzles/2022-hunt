from django.conf import settings
from django.urls import path

from hunt.deploy import views

gcloud_urlpatterns = []
if settings.HOST_ENV == 'gcloud':
    gcloud_urlpatterns += [
        # Google Cloud health check.
        path('_ah/warmup', views.gcloud_warmup_view),
    ]

site_access_urlpatterns = []
if settings.HUNT_WEBSITE_ACCESS_TOKEN:
    site_access_urlpatterns += [
        path(settings.HUNT_WEBSITE_ACCESS_TOKEN, views.grant_site_access_view),
    ]

common_urlpatterns = gcloud_urlpatterns + site_access_urlpatterns
