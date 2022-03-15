from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.cache import cache_control

from hunt.data_loader.auxiliary import get_auxiliary_data_file
from hunt.data_loader.chunks import get_chunk_file
from hunt.data_loader.puzzle import get_puzzle_data_file
from hunt.data_loader.round import get_round_data_file
from hunt.deploy.util import require_rd0_launch

from .common import should_show_solutions, require_puzzle_access, require_round_access
from .responses import XHttpResponse

@require_round_access(skip_cache=True, any_host=True)
def round_asset_view(request, variant, resource):
    """
    Views round or round solution asset.

    Note: These should only be used during development, as it unnecessarily
    uses Django views to serve a static asset.
    """
    team = request.team
    round = request.round

    is_protected = variant == 'solution'
    verify_resource_access(team, is_protected, resource)

    if resource.endswith('/'):
        resource += 'index.html'

    if is_protected:
        resource = f'{variant}/{resource}'

    data = get_round_data_file(round.url, resource)
    if not data:
        return XHttpResponse('Unknown file "%s/%s"' % (round.url, resource))
    return FileResponse(data)

@require_puzzle_access(allow_rd0_access=True, skip_cache=True, any_host=True)
def puzzle_asset_view(request, variant, resource):
    """
    Views puzzle or puzzle solution asset.

    Note: These should only be used during development, as it unnecessarily
    uses Django views to serve a static asset.
    """
    maybe_team = request.team
    puzzle = request.puzzle

    is_protected = variant in ('solution', 'posthunt')
    verify_resource_access(maybe_team, is_protected, resource)

    if resource.endswith('/'):
        resource += 'index.html'

    if is_protected:
        resource = f'{variant}/{resource}'

    data = get_puzzle_data_file(puzzle.url, resource)
    if not data:
        return XHttpResponse('Unknown file "%s/%s"' % (puzzle.url, resource))
    return FileResponse(data)

@require_rd0_launch
def chunk_view(request, resource):
    data = get_chunk_file(resource)
    if not data:
        return XHttpResponse('Unknown chunk "%s"' % (resource))
    return FileResponse(data)

@require_rd0_launch
def auxiliary_asset_view(request, bucket, resource):
    data = get_auxiliary_data_file(bucket, resource)
    if not data:
        return XHttpResponse('Unknown file "%s"' % (resource))
    return FileResponse(data)

def verify_resource_access(maybe_team, is_protected, resource):
    if is_protected and not should_show_solutions(maybe_team):
        return HttpResponseForbidden('Solutions are not available yet!')

    if resource.endswith('.tmpl'):
        return HttpResponseForbidden('No peeking!')

    if resource.endswith('.json') and not (maybe_team and maybe_team.is_internal):
        return HttpResponseForbidden('No peeking!')

    if resource.startswith('__build'):
        return HttpResponseForbidden('No peeking!')
