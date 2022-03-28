from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse

from spoilr.core.api.decorators import inject_team
from spoilr.core.models import Puzzle, HQUpdate

from hunt.app.core.assets.refs import get_round_static_path, get_auxiliary_static_path
from hunt.app.core.cache import cache_page_by_team
from hunt.app.core.constants import ROUND_RD0_URL, ROUND_RD3_HUB_URL, ROUND_RD1_URL, ROUND_RD2_URL, ROUND_ENDGAME_URL
from hunt.app.core.helpers import dispatch_discord_alert
from hunt.app.core.hosts import use_site_2_if_unlocked
from hunt.app.core.rewards import get_rewards, get_manuscrip_info
from hunt.app.core.story import get_story_summary
from hunt.deploy.util import require_rd0_launch, require_hunt_launch
from .common import get_shared_context, verify_team_accessible

# Note: This was redacted before making the repository public.
DISCORD_WEBHOOK = None

@require_rd0_launch
@inject_team(redirect_if_missing=False)
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def index_view(request):
    """View for hunt home page (when the hunt has started)."""
    context = get_shared_context(request.team)
    context['rd_root'] = get_round_static_path(ROUND_RD0_URL, variant='round')
    context['puzzles'] = (Puzzle.objects.filter(round__url=ROUND_RD0_URL)
        .order_by('order'))

    context['rd1_root'] = get_round_static_path(ROUND_RD1_URL, variant='round')
    context['rd2_root'] = get_round_static_path(ROUND_RD2_URL, variant='round')
    context['rd3_root'] = get_auxiliary_static_path(ROUND_RD3_HUB_URL)
    context['rd4_root'] = get_round_static_path(ROUND_ENDGAME_URL, variant='round')

    is_public_team = request.team and request.team.is_public

    if context['status'] == 'prelaunch':
        return render(request, 'top/prologue.tmpl', context)
    elif context['acts_unlocked']['act3'] and not is_public_team:
        return redirect(reverse('act3_hub'))
    elif context['acts_unlocked']['act2'] and not is_public_team:
        return redirect(reverse('round_view', args=(ROUND_RD2_URL,)))
    else:
        return redirect(reverse('round_view', args=(ROUND_RD1_URL,)))

@require_rd0_launch
@inject_team(redirect_if_missing=False)
@verify_team_accessible()
@cache_page_by_team()
def prologue_view(request):
    """View for hunt home page (when the hunt has started)."""
    context = get_shared_context(request.team)
    context['rd_root'] = get_round_static_path(ROUND_RD0_URL, variant='round')
    context['puzzles'] = (Puzzle.objects.filter(round__url=ROUND_RD0_URL)
        .order_by('order'))
    context['act'] = 'act0'

    return render(request, 'top/prologue.tmpl', context)

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def all_puzzles_view(request):
    context = get_shared_context(request.team)
    return render(request, 'top/all-puzzles.tmpl', context)

# Don't cache as it has timestamps.
@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
def updates_view(request):
    context = get_shared_context(request.team)
    context['updates'] = [
        update_obj(request.team, x) for x in HQUpdate.objects
            .filter(published=True)
            .filter(Q(team__isnull=True) | Q(team=request.team))
            .order_by('-publish_time')
      ]
    return render(request, 'top/updates.tmpl', context)

def update_obj(team, update):
    hidden = False
    if update.puzzle and not team.puzzleaccess_set.filter(puzzle=update.puzzle).exists():
        hidden = True
    return {
        'update': update,
        'timestamp': update.publish_time,
        'hidden': hidden,
        'puzzle': update.puzzle,
    }

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def story_view(request):
    context = get_shared_context(request.team)
    context['story'] = get_story_summary(context)
    return render(request, 'top/story.tmpl', context)

@require_rd0_launch
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def faq_view(request):
    """View to show frequently asked questions."""
    context = get_shared_context(request.team)
    if context['status'] == 'prelaunch':
        return render(request, 'top/faq-prologue.tmpl', context)
    else:
        return render(request, 'top/faq.tmpl', context)

@require_rd0_launch
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def stats_view(request):
    """View to show frequently asked questions."""
    context = get_shared_context(request.team)
    return render(request, 'top/stats.tmpl', context)

@require_rd0_launch
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def rewards_view(request):
    context = get_shared_context(request.team)
    context['rewards'] = get_rewards(context['rounds'])
    context['has_rewards'] = bool(len(context['rewards']))
    context['manuscrip_info'] = get_manuscrip_info(request.team)
    return render(request, 'top/rewards.tmpl', context)

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def sponsors_view(request):
    """View to show sponsor pages."""
    context = get_shared_context(request.team)
    return render(request, 'top/sponsors/list.tmpl', context)

@require_hunt_launch()
@inject_team()
@verify_team_accessible()
@use_site_2_if_unlocked
@cache_page_by_team()
def credits_view(request):
    """View to show credits page."""
    context = get_shared_context(request.team)
    return render(request, 'top/credits.tmpl', context)

@require_hunt_launch()
@inject_team()
@use_site_2_if_unlocked
@cache_page_by_team()
def sponsor_details_view(request, sponsor_name):
    """View to show details for a specific sponsor."""
    context = get_shared_context(request.team)
    return render(request, f'top/sponsors/{sponsor_name}.sponsor.tmpl', context)

def archive_pages_view(request):
    return render(request, f'top/archive-pages.tmpl')

@require_hunt_launch()
@inject_team(redirect_if_missing=False)
@verify_team_accessible()
def missing_documents_view(request):
    context = get_shared_context(request.team)
    return render(request, f'top/missing_documents.tmpl', context)

def ratelimited_error_view(request, exception):
    body = 'This request was ratelimited: ' + str(request) \
           + '\nSession key: ' + request.session.session_key \
           + "\nTeam: " + request.user.team.name \
            + "\nBody: " + request.body.decode("utf-8")
    dispatch_discord_alert(DISCORD_WEBHOOK,
                           body,
                           username='Ratelimit Bot')
    return JsonResponse({'error': 'ratelimited'}, status=429)
