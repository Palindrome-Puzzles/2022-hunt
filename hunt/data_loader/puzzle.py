from django.conf import settings

from hunt.app.core.cache import memoized_cache

from ._common import allow_compiled_version, importlib_resources

cache_puzzle_data_text = memoized_cache('get_puzzle_data_text') if settings.HUNT_ENABLE_FILE_CACHING else lambda view_func: view_func
cache_puzzle_asset_urls = memoized_cache('get_puzzle_asset_urls') if settings.HUNT_ENABLE_FILE_CACHING else lambda view_func: view_func

@cache_puzzle_data_text
@allow_compiled_version
def get_puzzle_data_text(puzzle_url, *path):
    """
    Returns the content of a puzzle data file as text, or None if the file does
    not exist.
    """
    path = get_all_puzzle_data().joinpath(puzzle_url, *path)
    return path.read_text(encoding='utf8') if path.exists() else None

def get_puzzle_data_file(puzzle_url, *path):
    """
    Returns the content of a puzzle data file as bytes, or None if the file does
    not exist.
    """
    path = get_all_puzzle_data().joinpath(puzzle_url, *path)
    return path.open('rb') if path.exists() else None

@cache_puzzle_asset_urls
def get_puzzle_asset_urls():
    """
    Returns a list of all puzzle URLs for which a puzzle asset blob exists.
    """
    return sorted(map(
        lambda path: path.name,
        filter(
            lambda path: path.is_dir(),
            get_all_puzzle_data().glob('*'))))

def get_all_puzzle_data():
    package_name = settings.HUNT_DATA_PACKAGE_NAME
    puzzle_data_prefix = settings.HUNT_DATA_PACKAGE_PUZZLE_DATA

    return importlib_resources.files(package_name).joinpath(puzzle_data_prefix)
