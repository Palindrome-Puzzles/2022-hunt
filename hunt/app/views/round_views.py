import ast, collections, logging, random, string
from more_itertools import partition

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, reverse
from django.template import Template, Context

from spoilr.core.api.decorators import inject_team, get_inaccessible_round_response
from spoilr.core.models import Puzzle, Round

from hunt.data_loader.auxiliary import get_auxiliary_data_text
from hunt.data_loader.round import get_round_data_text
from hunt.deploy.util import require_hunt_launch

from hunt.app.core.assets.refs import get_round_static_path
from hunt.app.core.assets.resolvers import create_round_url_resolver
from hunt.app.core.cache import cache_page_by_team
from hunt.app.core.constants import ROUND_RD0_URL, ROUND_EVENTS_URL, ROUND_RD3_HUB_URL, ROUND_RD3_URLS, ROUND_RD3_META_URL, ROUND_ENDGAME_URL
from hunt.app.core.assets.rewriter import rewrite_relative_paths
from hunt.app.core.helpers import omit
from hunt.app.core.hosts import use_site_2_if_unlocked
from hunt.app.core.puzzles import is_act3_unlocked
from .common import get_shared_context, require_round_access, get_round_accesses, get_round_summary, get_act_for_round
from .responses import XHttpResponse

logger = logging.getLogger(__name__)

@require_round_access()
def round_view(request):
    """View for a round's main page."""
    # No round page for prologue / endgame.
    if request.round.url in (ROUND_RD0_URL, ROUND_EVENTS_URL, ROUND_ENDGAME_URL):
        return get_inaccessible_round_response(request.round.url)

    round = request.round

    context = get_round_context(request, request.team, round)
    context['rd_root'] = get_round_static_path(round.url, variant='round')

    style = get_round_data_text(round.url, 'style.css')
    common_style = get_round_data_text(round.url, 'round_common.css')
    url_resolver = create_round_url_resolver(round.url, 'round')

    raw_manifest = get_round_data_text(round.url, 'manifest.py')
    sticker_manifest = ast.literal_eval(raw_manifest) if raw_manifest else None

    context_obj = Context(context)
    context['round_style'] = rewrite_relative_paths(
        Template(style).render(context_obj), url_resolver) if style else None
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), url_resolver) if common_style else None
    context['sticker_info'] = collate_sticker_info(sticker_manifest, context_obj['round_info'], context_obj['rounds'])
    context['is_breakglass_access'] = not request.round_access

    return render(request, 'round_files/%s/round.tmpl' % (round.url), context)

@require_round_access()
def round_subview(request, subview):
    round = request.round

    context = get_round_context(request, request.team, round)
    context['rd_root'] = get_round_static_path(round.url, variant='round')

    common_style = get_round_data_text(round.url, 'round_common.css')
    url_resolver = create_round_url_resolver(round.url, 'round')

    context_obj = Context(context)
    context['round_common_style'] = rewrite_relative_paths(
        Template(common_style).render(context_obj), url_resolver) if common_style else None
    context['is_breakglass_access'] = not request.round_access

    path = ['round_files', round.url, f'{subview}.tmpl']
    return render(request, '/'.join(path), context)

@require_hunt_launch()
@inject_team()
@use_site_2_if_unlocked
@cache_page_by_team()
def act3_hub_view(request):
    context = get_shared_context(request.team)
    all_act3_rounds = ROUND_RD3_URLS + [ROUND_RD3_META_URL, ROUND_ENDGAME_URL]

    unlocked_round_urls = set(round_info['round'].url for round_info in context['rounds'])
    unlocked = is_act3_unlocked(unlocked_round_urls)
    if not unlocked and not request.user.is_staff:
        return HttpResponseNotFound('Not found')

    if settings.HUNT_ROUND_BREAKGLASS_UNLOCKS_ENABLED and request.user.is_staff and not request.impersonating:
        if 'count' in request.GET:
            unlocked_round_urls = all_act3_rounds[:int(request.GET['count'])]

    raw_manifest = get_auxiliary_data_text(ROUND_RD3_HUB_URL, 'manifest.py')
    sticker_manifest = ast.literal_eval(raw_manifest) if raw_manifest else None

    context['is_breakglass_access'] = not unlocked
    context['sticker_info'] = collate_round_sticker_info(
        sticker_manifest,
        Round.objects.filter(url__in=all_act3_rounds),
        unlocked_round_urls)
    context['act'] = 'act3'

    return render(request, 'top/act3_hub.tmpl', context)

def get_round_context(request, team, round):
    breakglass_access = None
    if settings.HUNT_ROUND_BREAKGLASS_UNLOCKS_ENABLED and request.user.is_staff and not request.impersonating:
        breakglass_access = {
            'puzzle_count': int(request.GET['puzzle_count'], 10),
            'meta_count': int(request.GET.get('meta', 10)),
            'solved': request.GET.get('solved', '1') == '1',
        } if 'puzzle_count' in request.GET else None

    context = get_shared_context(team)
    context['round_info'] = get_round_summary(team, round, breakglass_access)
    context['is_breakglass_access'] = not request.round_access
    context['act'] = get_act_for_round(round)
    return context

def collate_sticker_info(sticker_manifest, round_info, round_infos):
    unlocked_puzzles = {
        puzzle_info['puzzle'].external_id: puzzle_info
        for puzzle_info in round_info['puzzles']
    }

    round_puzzles = Puzzle.objects.filter(round=round_info['round']).order_by('order')
    non_metas_gen, metas_gen = partition(lambda puzzle: puzzle.is_meta, round_puzzles)
    non_metas, metas = list(non_metas_gen), list(metas_gen)

    unlocked_non_metas_gen, unlocked_metas_gen = partition(lambda puzzle_info: puzzle_info['puzzle'].is_meta, round_info['puzzles'])
    unlocked_non_metas, unlocked_metas = list(unlocked_non_metas_gen), list(unlocked_metas_gen)

    stickers = []
    if sticker_manifest:
        sticker_counter = 0
        puzzle_counter = 0
        for entry in sticker_manifest:
            if 'puzzle' in entry:
                is_meta = 'is_meta' in entry and entry['is_meta']
                if is_meta:
                    assert 'image' in entry, 'image required for meta puzzles'
                else:
                    puzzle_counter += 1

                source = metas if is_meta else non_metas
                puzzle = source[entry['puzzle'] - 1]
                if puzzle.external_id in unlocked_puzzles:
                    sticker_counter += 1
                    stickers.append({
                        **entry,
                        'sticker_counter': sticker_counter,
                        'image': entry['image'] if 'image' in entry else str(puzzle_counter),
                        'wordmark': (get_round_static_path(entry['wordmark'], variant='round') + 'images/wordmark.png') if 'wordmark' in entry else None,
                        'puzzle': puzzle,
                        'solved': unlocked_puzzles[puzzle.external_id]['solved'],
                    })
                elif 'locked_image' in entry and entry['locked_image']:
                    sticker_counter += 1
                    stickers.append({
                        **omit(entry, 'puzzle'),
                        'sticker_counter': sticker_counter,
                        'image': entry['locked_image'],
                    })

            else:
                passes = True
                image_override = entry.get('image')
                if 'predicate' in entry:
                    if 'non_meta_count' in entry['predicate'] and len(unlocked_non_metas) < entry['predicate']['non_meta_count']:
                        passes = False

                    if 'puzzle' in entry['predicate']:
                        source = metas if entry.get('is_meta') else non_metas
                        if not source[entry['predicate']['puzzle'] - 1].external_id in unlocked_puzzles:
                            if 'locked_image' in entry:
                                image_override = entry['locked_image']
                            else:
                                passes = False

                    if 'act3' in entry['predicate']:
                        unlocked_round_urls = set(x['round'].url for x in round_infos)
                        if not is_act3_unlocked(unlocked_round_urls):
                            passes = False

                if passes:
                    sticker_counter += 1
                    stickers.append({
                        **entry,
                        'sticker_counter': sticker_counter,
                        'image': image_override,
                        'link': reverse(*entry['link']) if 'link' in entry else None,
                    })

    sticker_info = {
        'stickers': stickers,
        'has_meta': len(unlocked_metas) > 0,
    }
    return sticker_info

def collate_round_sticker_info(sticker_manifest, rounds, unlocked_round_urls):
    round_lookup = {
        round.url: round for round in rounds
    }
    stickers = []
    if sticker_manifest:
        counter_by_category = collections.defaultdict(int)
        for entry in sticker_manifest:
            if entry['round'] in unlocked_round_urls:
                counter_by_category[entry['category']] += 1
                stickers.append({
                    **entry,
                    'round': round_lookup[entry['round']],
                    'sticker_counter': counter_by_category[entry['category']],
                    'link': reverse(*entry['link']) if 'link' in entry else None,
                })
            elif 'locked_image' in entry:
                counter_by_category[entry['category']] += 1
                stickers.append({
                    **omit(entry, 'round'),
                    'sticker_counter': counter_by_category[entry['category']],
                    'image': entry['locked_image'],
                })

    sticker_info = {
        'stickers': stickers,
    }
    return sticker_info
