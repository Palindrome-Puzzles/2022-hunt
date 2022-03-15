from django.urls import path, re_path

from . import views

app_name = 'spoilr.events'
urlpatterns = [
    re_path('^export/(?P<event_url>[^/]+)/?$', views.export_view, name='export'),
]
