import urllib.parse
from functools import wraps

from .refs import get_puzzle_static_path, get_round_static_path

def create_round_url_resolver(round_url, variant):
    """
    Creates a resolver for URLs in round static assets.

    `variant` can be either `round` for the round's assets, or `solution` for
    the round's solution assets.

    Some static assets at the root directory of the round are served from the
    URL `/round/<round_url>/` instead of their true location in the
    round-specific static directory. This returns a resolver that transforms any
    relative URLs so they still work.
    """
    assert variant in ('round', 'solution')

    round_prefix = get_round_static_path(round_url, variant='round')
    solution_prefix = get_round_static_path(round_url, variant='solution')

    protected_variants = ('solution')
    prefix_by_variant = {
        'round': round_prefix,
        'solution': solution_prefix,
    }
    return asset_url_resolver(f'round {round_url}', 'round', variant, prefix_by_variant, protected_variants)

def create_puzzle_url_resolver(puzzle_url, variant, *, can_access_posthunt):
    """
    Creates a resolver for URLs in puzzle static assets.

    `variant` can be either `puzzle` for the puzzle's assets, `solution` for the
    puzzle's solution assets, or `posthunt` for the puzzle's posthunt assets.

    Some static assets at the root directory of the puzzle are served from the
    URL `/puzzle/<puzzle_url>/` instead of their true location in the
    puzzle-specific static directory. This returns a resolver that transforms
    any relative URLs so they still work.

    `can_access_posthunt` indicates whether the current team can access posthunt
    assets from the puzzle bundle. This should only be True for public teams or
    access after the hunt is complete.
    """
    assert variant in ('puzzle', 'solution', 'posthunt')

    puzzle_prefix = get_puzzle_static_path(puzzle_url, variant='puzzle')
    posthunt_prefix = get_puzzle_static_path(puzzle_url, variant='posthunt')
    solution_prefix = get_puzzle_static_path(puzzle_url, variant='solution')

    protected_variants = ('solution', 'posthunt')
    prefix_by_variant = {
        'puzzle': puzzle_prefix,
        'posthunt': posthunt_prefix,
        'solution': solution_prefix,
    }
    return asset_url_resolver(f'puzzle {puzzle_url}', 'puzzle', variant, prefix_by_variant, protected_variants, can_access_posthunt=can_access_posthunt)

def asset_url_resolver(context, default_variant, variant, prefix_by_variant, protected_variants, *, can_access_posthunt=False):
    """
    Helper that takes advantage of similarities between the directory structure
    of puzzle and round assets to share code.

    See callers for what the arguments mean.
    """
    @_ignore_absolute_urls
    @_strip_dotdots_at_beginning(max_allowed=1)
    def url_resolver(resource_url, number_of_dotdots):
        if variant in protected_variants:
            # Canonicalize references from one protected variant to another.
            chosen_variant = variant
            if number_of_dotdots == 1 and any(resource_url.startswith(f'{protected_variant}/') for protected_variant in protected_variants):
                slash_loc = resource_url.index('/')
                chosen_variant = resource_url[:slash_loc]
                resource_url = resource_url[slash_loc+1:]
                number_of_dotdots -= 1

            # Protected variants are allowed to refer back to non-protected assets.
            if number_of_dotdots:
                prefix = prefix_by_variant[default_variant]
            else:
                prefix = prefix_by_variant[chosen_variant]
        else:
            chosen_variant = variant
            if number_of_dotdots:
                raise Exception(f'{context} ({variant}) has an invalid URL: `{resource_url}`')
            if any(resource_url.startswith(f'{protected_variant}/') for protected_variant in protected_variants):
                # Special case to allow puzzles to access posthunt content.
                if resource_url.startswith('posthunt/') and can_access_posthunt:
                    slash_loc = resource_url.index('/')
                    chosen_variant = resource_url[:slash_loc]
                    resource_url = resource_url[slash_loc+1:]
                else:
                    raise Exception(f'{context} ({variant}) is trying to access protected asset: `{resource_url}`')
            prefix = prefix_by_variant[chosen_variant]
        return urllib.parse.urljoin(prefix, resource_url)
    return url_resolver

def _ignore_absolute_urls(relative_url_resolver_fn):
    """
    Intercepts absolute URLs and absolute paths and makes the resolver pass them
    through unchanged.
    """
    @wraps(relative_url_resolver_fn)
    def url_resolver(url):
        parsed = urllib.parse.urlsplit(url)
        if parsed.netloc or parsed.path.startswith('/'):
            return url
        return relative_url_resolver_fn(url)
    return url_resolver

def _strip_dotdots_at_beginning(max_allowed):
    """
    Decorator that strips `..` from the beginning of the path and counts them.
    The stripped path count is passed to the decorated function.

    Also asserts no `..` are anywhere else within the path.
    """
    def decorator(url_resolver_fn):
        @wraps(url_resolver_fn)
        def url_resolver(url):
            parsed = urllib.parse.urlsplit(url)
            path = parsed.path
            assert not path.startswith('/')

            number_of_dotdots = 0
            while path.startswith('../') or path == '..':
                number_of_dotdots += 1
                path = path[3:]

            if '..' in path:
                raise Exception(f'Invalid path {path} has ".." in the middle')

            if number_of_dotdots > max_allowed:
                raise Exception(f'Too many ".." at the start for path {path}')

            parsed = parsed._replace(path=path)
            return url_resolver_fn(urllib.parse.urlunsplit(parsed), number_of_dotdots)
        return url_resolver
    return decorator
