import hashlib, urllib.parse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static
from django.urls import reverse

def get_puzzle_static_path(puzzle_url, variant):
    """
    Returns the base path for the assets for the specified puzzle and variant.

    `variant` can be either `puzzle` for the puzzle assets, `solution` for the
    puzzle's solution assets, or `posthunt` for the puzzle's posthunt assets.

    The returned path can either be the Django view to dynamically load the
    asset, or the path to the static file where the asset is deployed.
    """
    return _static_path(
        asset_type='puzzle', asset_view='puzzle_asset', url=puzzle_url, variant=variant)

def get_round_static_path(round_url, variant):
    """
    Returns the base path for the assets for the specified round and variant.

    `variant` can be either `round` for the round assets, or `solution` for the
    round's solution assets.

    The returned path can either be the Django view to dynamically load the
    asset, or the path to the static file where the asset is deployed.
    """
    return _static_path(
        asset_type='round', asset_view='round_asset', url=round_url, variant=variant)

def get_auxiliary_static_path(bucket):
    """
    Returns the base path for the auxiliary assets in the specified bucket.

    The returned path can either be the Django view to dynamically load the
    asset, or the path to the static file where the asset is deployed.
    """
    return _static_path(
        asset_type='auxiliary', asset_view='auxiliary_asset', url=bucket)

def _static_path(*, asset_type, asset_view, url, variant=None):
    if not settings.DEBUG and not settings.HUNT_ASSETS_SERVE_STATICALLY:
        raise ImproperlyConfigured('HUNT_ASSETS_SERVE_STATICALLY must be True when not in debug mode')

    if settings.HUNT_ASSETS_SERVE_STATICALLY:
        key = hash_asset_type(asset_type, url, variant or asset_type)
        path = urllib.parse.urljoin(settings.HUNT_ASSETS_STATIC_PREFIX, key + '/')
        return urllib.parse.urljoin(settings.STATIC_URL, path)

    if variant:
        return reverse(asset_view, args=(url, variant, ''))
    return reverse(asset_view, args=(url, ''))

def hash_asset_type(asset_type, url, variant):
    # TODO(sahil): Consider using Django utils for this.
    # Throw all our entropy and generate some hash for the asset type. And then
    # just pick the second half of it because we don't want URLs to be too long.
    m = hashlib.sha256()
    m.update(to_bytes(settings.SECRET_KEY))
    m.update(to_bytes(asset_type))
    m.update(to_bytes(url))
    m.update(to_bytes(variant))
    return m.hexdigest()[-16:]

def to_bytes(string):
    return string.encode('utf-8')

def from_bytes(bytes):
    return bytes.decode('utf-8')
