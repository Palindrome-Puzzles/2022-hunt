from django.urls import path, re_path

from .views import dashboard_views, graph_views

app_name = 'spoilr.progress'
urlpatterns = [
    path('teams/', dashboard_views.teams_view, name='teams'),
    path('puzzles/', dashboard_views.puzzles_view, name='puzzles'),
    re_path('puzzle/(?P<puzzle_id>[0-9]+)/', dashboard_views.puzzle_view, name='puzzle_view'),
    path('interactions/', dashboard_views.interactions_view, name='interactions'),
    re_path('^team/(?P<team_username>[^/]+)/$', dashboard_views.team_view, name='team'),

    path('solves/', graph_views.solve_graph_view, name='solves'),
    path('solve_data.json', graph_views.solve_data_json_view, name='solve_data'),
]
