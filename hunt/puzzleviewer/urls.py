from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path('^$', views.puzzle_list_view, name='puzzle_list'),
    re_path('^(?P<puzzle_url>[^/]+)/$', views.puzzle_view, name='puzzle'),
    re_path('^(?P<puzzle_url>[^/]+)/solution/?$', views.solution_view, name='solution'),
    re_path('^(?P<puzzle_url>[^/]+)/posthunt/?$', views.posthunt_view, name='posthunt'),
    re_path('^(?P<puzzle_url>[^/]+)/(?P<resource>.*)$', views.asset_view, name='asset'),
]
