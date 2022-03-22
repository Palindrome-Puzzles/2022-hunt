from django.conf import settings
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView

from hunt.app.views import asset_views, auth_views, contact_views, events_views, magic_views, manuscrip_views, puzzle_views, puzzle_hint_views, puzzle_submit_views, round_views, top_views
from hunt.app.core.constants import PUZZLE_ENDGAME_URL, ROUND_RD2_URL

# TODO(sahil): Add survey and contact back here, and delegate view logic to
# spoilr.

NOOP_VIEW = lambda request: HttpResponse('OK')

urlpatterns = []

# Standard puzzles and rounds handling.
urlpatterns += [
    re_path('^puzzle/(?P<puzzle>[^/]+)/$', puzzle_views.puzzle_view, name='puzzle_view'),
    re_path('^puzzle/(?P<puzzle>[^/]+)/solution/$', puzzle_views.solution_view, name='puzzle_solution'),
    re_path('^round/(?P<round>[^/]+)/$', round_views.round_view, name='round_view'),

    re_path('^embed/submit/puzzle/(?P<puzzle>[^/]+)/$', puzzle_submit_views.submit_puzzle_view, name='puzzle_submit_embed'),

    re_path('^submit/hint/(?P<puzzle>[^/]+)/$', puzzle_hint_views.hints_view, name='puzzle_hints', kwargs={'embed': False}),
    re_path('^submit/hint/(?P<puzzle>[^/]+)/embed$', puzzle_hint_views.hints_view, name='puzzle_hints_embed', kwargs={'embed': True}),
]

# Other puzzle related URLs.
urlpatterns += [
    path('prologue/', top_views.prologue_view, name='prologue'),
    path('pen-station/', round_views.act3_hub_view, name='act3_hub'),
    path('tollbooth/', puzzle_views.puzzle_view, kwargs={'puzzle': PUZZLE_ENDGAME_URL}, name='endgame_puzzle'),
    path('round/the-ministry/book-reports/', round_views.round_subview, kwargs={'round': ROUND_RD2_URL, 'subview': 'book_reports'}, name='act2_scav_hunt'),

    re_path('^magic/release/interaction/(?P<interaction>[^/]+)/$', magic_views.release_interaction_view, name='magic_release_interaction'),
    re_path('^release/act2/$', magic_views.release_act1_view),
    re_path('^release/unlock-more/$', magic_views.increase_radius_view),
    path('release/pen-station/', magic_views.unlock_pen_station_view),
    path('release/pen-station/1', magic_views.unlock_more_1_view),
    path('release/pen-station/2', magic_views.unlock_more_2_view),
    path('release/pen-station/next', magic_views.unlock_more_3_view),

    path('admin/email-unlocks', magic_views.email_to_unlock_more_view),
]

# Dynamic loaders for puzzles and rounds assets.
#
# These are only used when the `HUNT_ASSETS_SERVE_STATICALLY` setting is `False`.
# They require Django to authenticate, fetch, and return the asset in
# Python-land and so are slower than deploying assets properly. However, it's a
# useful trick at development time, as we don't need to re-deploy assets to see
# changes.
#
# The transformed paths are designed to break relative paths if asset rewriting
# isn't working, so that puzzle/round authors notice and address the issue. That
# way, no issues get accidentally masked and then bite us in our production
# website.
if settings.DEBUG:
    urlpatterns += [
        re_path('^puzzle/(?P<puzzle>[^/]+)/s__(?P<variant>[^/]+)/(?P<resource>.*)$', asset_views.puzzle_asset_view, name='puzzle_asset'),
        re_path('^round/(?P<round>[^/]+)/s__(?P<variant>[^/]+)/(?P<resource>.*)$', asset_views.round_asset_view, name='round_asset'),
        re_path('^chunks/(?P<resource>.*)$', asset_views.chunk_view, name='chunk'),
        re_path('^auxiliary/(?P<bucket>[^/]+)/(?P<resource>.*)$', asset_views.auxiliary_asset_view, name='auxiliary_asset'),
    ]

# Solver-accessible hunt website URLs.
urlpatterns += [
    path('', top_views.index_view, name='index'),
    path('puzzles/', top_views.all_puzzles_view, name='all_puzzles'),
    path('archive/', top_views.story_view, name='story'),
    path('updates/', top_views.updates_view, name='updates'),

    path('contact/', contact_views.contact_view, name='contact'),
    path('faq/', top_views.faq_view, name='faq'),
    path('stats/', top_views.stats_view, name='stats'),
    path('rewards/', top_views.rewards_view, name='rewards_drawer'),
    path('missing-documents/', top_views.missing_documents_view, name='missing_documents'),
    path('credits/', top_views.credits_view, name='credits'),

    path('events/', events_views.events_view, name='events'),
    re_path('^events/(?P<event_url>[^/]+)/?$', events_views.events_register_view, name='events_register'),
    re_path('^events/(?P<event_url>[^/]+)/unregister/?$', events_views.events_unregister_view, name='events_unregister'),

    path('sponsors/', top_views.sponsors_view, name='sponsors'),
    re_path('^sponsor/(?P<sponsor_name>[^/]+)/$', top_views.sponsor_details_view, name='sponsor_details'),

    path('manuscrip/spend/', manuscrip_views.spend_view, name='manuscrip_spend'),
]

# SSO login URL.
urlpatterns += [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('auth/', auth_views.authorize_view, name='authorize'),
    path('update_registration/', auth_views.update_registration_view, name='update_registration'),
]

# Extra view to use for referencing the root of the site. This is never visited
# (as other views are higher priority) and should be kept last!
urlpatterns += [
    path('', NOOP_VIEW, name='host_resolve_root')
]
