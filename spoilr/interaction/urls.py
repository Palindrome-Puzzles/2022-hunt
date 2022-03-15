from django.conf import settings
from django.urls import path, re_path

from . import views

app_name = 'spoilr.interaction'
urlpatterns = [
    path('resolve/', views.resolve_view, name='resolve'),
    path('danger-release/', views.danger_release_view, name='danger_release'),

    path('answer/cancel/', views.resolve_answer_view, name='resolve_answer'),

    path('', views.dashboard_view, name='dashboard'),
    re_path('^(?P<interaction_url>[^/]+)/$', views.interaction_view, name='interaction'),
    re_path('^(?P<interaction_url>[^/]+)/(?P<team_username>[^/]+)/$', views.details_view, name='details'),
]
