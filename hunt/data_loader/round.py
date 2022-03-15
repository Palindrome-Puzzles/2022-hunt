from django.conf import settings

from hunt.app.core.cache import memoized_cache

from ._common import allow_compiled_version, importlib_resources

cache_round_data_text = memoized_cache('get_round_data_text') if settings.HUNT_ENABLE_FILE_CACHING else lambda view_func: view_func
cache_round_asset_urls = memoized_cache('get_round_asset_urls') if settings.HUNT_ENABLE_FILE_CACHING else lambda view_func: view_func

@cache_round_data_text
@allow_compiled_version
def get_round_data_text(round_url, *path):
    """
    Returns the content of a round data file as text, or None if the file does
    not exist.
    """
    path = get_all_round_data().joinpath(round_url, *path)
    return path.read_text(encoding='utf8') if path.exists() else None

def get_round_data_file(round_url, *path):
    """
    Returns the content of a round data file as bytes, or None if the file does
    not exist.
    """
    path = get_all_round_data().joinpath(round_url, *path)
    return path.open('rb') if path.exists() else None

@cache_round_asset_urls
def get_round_asset_urls():
    """
    Returns a list of all round names for which any puzzle data file exists.
    """
    return sorted(map(
        lambda path: path.name,
        filter(
            lambda path: path.is_dir(),
            get_all_round_data().glob('*'))))

def get_all_round_data():
    package_name = settings.HUNT_DATA_PACKAGE_NAME
    round_data_prefix = settings.HUNT_DATA_PACKAGE_ROUND_DATA

    return importlib_resources.files(package_name).joinpath(round_data_prefix)
