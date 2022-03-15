from django.urls import path, re_path

from . import views

app_name = 'spoilr.hints'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    re_path('^(?P<puzzle>[^/]+)/hints/$', views.canned_hints_view, name='canned'),
    path('respond/', views.respond_view, name='respond'),
]
