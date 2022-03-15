import datetime, hashlib, json, urllib.parse

from django.conf import settings
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render, reverse
from django.template import Template, Context
from django.utils.html import escape
from django.utils.timezone import now
from django.views.decorators.cache import cache_control

from spoilr.core.api.answer import canonicalize_puzzle_answer, canonicalize_puzzle_answer_display
from spoilr.core.api.decorators import inject_team

from hunt.app.core.assets.refs import get_puzzle_static_path
from hunt.app.core.assets.resolvers import asset_url_resolver, create_puzzle_url_resolver
from hunt.app.core.assets.rewriter import rewrite_relative_paths
from hunt.data_loader.puzzle import get_puzzle_asset_urls, get_puzzle_data_text, get_puzzle_data_file

@inject_team(require_internal=True)
def puzzle_list_view(request):
    urls = get_puzzle_asset_urls()
    metadatas = map(lambda url: get_metadata(url), urls)
    context = {
        'puzzles': sorted([
            { 'url': metadata['puzzle_slug'], 'title': metadata['puzzle_title'] }
            for metadata in metadatas if metadata
        ], key=lambda info: info['title'])
    }
    return render(request, 'puzzle-list.html', context)

@inject_team(require_internal=True)
def puzzle_view(request, puzzle_url):
    metadata = get_metadata(puzzle_url)
    config = get_config(puzzle_url)
    html = get_puzzle_data_text(puzzle_url, 'index.html')
    style = get_puzzle_data_text(puzzle_url, 'style.css')
    if not metadata or html == None:
        return HttpResponseBadRequest(f'Unknown puzzle "{escape(puzzle_url)}"')

    has_posthunt = bool(get_puzzle_data_text(puzzle_url, 'posthunt', 'index.html'))
    answer_sha256 = get_answer_sha256(metadata['answer'])

    raw_pseudo = config.get('pseudo') if config else {}
    pseudo_sha256 = {
        get_answer_sha256(answer): response for answer, response in raw_pseudo.items()
    }

    puzzle_url_resolver = create_hybrid_url_resolver(puzzle_url, 'puzzle')
    context = {
        'auth': request.team.teamdata.auth,
        'puzzle_info': {
            'unlock_time': now() - datetime.timedelta(minutes=60),
            'full_path': reverse('puzzle_view', args=(puzzle_url,)),
            'static_directory': get_puzzle_static_directory(puzzle_url),
        },
        'puzzle_external_id': metadata['puzzle_idea_id'],
        'puzzle_url': puzzle_url,
        'puzzle_title': metadata['puzzle_title'],
        'answer_sha256': answer_sha256,
        'pseudo_sha256': json.dumps(pseudo_sha256),
        'has_posthunt': has_posthunt,
        'rd_root': 'dummy/',
        'serve_css_from_file': settings.HUNT_SERVE_CSS_FROM_FILE
    }
    context_obj = Context(context)
    context['index_html'] = rewrite_relative_paths(
        Template(html).render(context_obj), puzzle_url_resolver)
    context['puzzle_style'] =  rewrite_relative_paths(
        Template(style).render(context_obj), puzzle_url_resolver) if style else None
    return render(request, 'puzzle.html', context)

@inject_team(require_internal=True)
def posthunt_view(request, puzzle_url):
    metadata = get_metadata(puzzle_url)
    html = get_puzzle_data_text(puzzle_url, 'posthunt', 'index.html')
    style = get_puzzle_data_text(puzzle_url, 'posthunt', 'style.css')
    if not metadata or html == None:
        return HttpResponseBadRequest(f'Unknown puzzle "{escape(puzzle_url)}"')

    puzzle_url_resolver = create_hybrid_url_resolver(puzzle_url, 'posthunt')
    context = {
        'auth': request.team.teamdata.auth,
        'puzzle_info': {
            'unlock_time': now() - datetime.timedelta(minutes=60),
            'full_path': reverse('puzzle_view', args=(puzzle_url,)),
            'static_directory': get_puzzle_static_directory(puzzle_url),
        },
        'puzzle_external_id': metadata['puzzle_idea_id'],
        'puzzle_url': puzzle_url,
        'puzzle': {'full_path': reverse('puzzle_view', args=(puzzle_url,))},
        'puzzle_title': metadata['puzzle_title'],
        'rd_root': 'dummy/',
    }
    context_obj = Context(context)
    context['index_html'] = rewrite_relative_paths(
        Template(html).render(Context(context)), puzzle_url_resolver)
    context['puzzle_style'] =  rewrite_relative_paths(
        Template(style).render(context_obj), puzzle_url_resolver) if style else None
    return render(request, 'posthunt.html', context)

@inject_team(require_internal=True)
def solution_view(request, puzzle_url):
    metadata = get_metadata(puzzle_url)
    html = get_puzzle_data_text(puzzle_url, 'solution', 'index.html')
    style = get_puzzle_data_text(puzzle_url, 'solution', 'style.css')
    if not metadata or html == None:
        return HttpResponseBadRequest(f'Unknown puzzle "{escape(puzzle_url)}"')

    puzzle_url_resolver = create_hybrid_url_resolver(puzzle_url, 'solution')
    context = {
        'auth': request.team.teamdata.auth,
        'puzzle_info': {
            'full_path': reverse('puzzle_view', args=(puzzle_url,)),
            'static_directory': get_puzzle_static_directory(puzzle_url),
        },
        'puzzle_external_id': metadata['puzzle_idea_id'],
        'puzzle_url': puzzle_url,
        'puzzle': {'full_path': reverse('puzzle_view', args=(puzzle_url,))},
        'puzzle_title': metadata['puzzle_title'],
        'answer_display': canonicalize_puzzle_answer_display(metadata['answer']),
        'credits': metadata['credits'],
        'rd_root': 'dummy/',
    }
    context_obj = Context(context)
    context['index_html'] = rewrite_relative_paths(
        Template(html).render(Context(context)), puzzle_url_resolver)
    context['puzzle_solution_style'] =  rewrite_relative_paths(
        Template(style).render(context_obj), puzzle_url_resolver) if style else None
    return render(request, 'solution.html', context)

@inject_team(require_internal=True)
@cache_control(private=True, max_age=60)
def asset_view(request, puzzle_url, resource):
    if resource.endswith('/'):
        resource += 'index.html'
    data = get_puzzle_data_file(puzzle_url, resource)
    if not data:
        return HttpResponseBadRequest('Unknown file "%s/%s"' % (escape(puzzle_url), escape(resource)))
    return FileResponse(data)

def get_metadata(puzzle_url):
    metadata = get_puzzle_data_text(puzzle_url, 'metadata.json')
    if metadata:
        return json.loads(metadata)
    return None

def get_config(puzzle_url):
    config = get_puzzle_data_text(puzzle_url, 'config.json')
    if config:
        return json.loads(config)
    return None

def get_answer_sha256(answer):
    answer_hasher = hashlib.sha256()
    answer_hasher.update(canonicalize_puzzle_answer(answer).encode('utf-8'))
    return answer_hasher.hexdigest()

def create_hybrid_url_resolver(puzzle_url, variant):
    # If static, use ordinary puzzle resolvers so that we use public keyed
    # assets, and copy+paste works in staging puzzleviewer.
    if settings.HUNT_ASSETS_SERVE_STATICALLY:
        return create_puzzle_url_resolver(puzzle_url, variant)

    # Otherwise, for now use a fallback URL resolution that is handled by
    # asset_view above. Long-term, we need to have puzzleviewer use a special
    # team that has access to every puzzle though.
    protected_variants = ('solution', 'posthunt')
    prefix_by_variant = {
        'puzzle': reverse('asset', args=(puzzle_url, '')),
        'posthunt': reverse('asset', args=(puzzle_url, 'posthunt/')),
        'solution': reverse('asset', args=(puzzle_url, 'solution/')),
    }
    return asset_url_resolver(
        f'puzzle {puzzle_url}', 'puzzle', variant, prefix_by_variant, protected_variants)

def get_puzzle_static_directory(puzzle_url):
    if settings.HUNT_ASSETS_SERVE_STATICALLY:
        return get_puzzle_static_path(puzzle_url, variant='puzzle')
    else:
        return reverse('asset', args=(puzzle_url, ''))
