from django.conf import settings

from ._common import importlib_resources

def get_chunk_file(*path):
    """
    Returns the content of a chunk as bytes, or None if the file does not exist.
    """
    path = get_all_shared_chunks().joinpath(*path)
    return path.open('rb') if path.exists() else None

def get_all_shared_chunks():
    package_name = settings.HUNT_DATA_PACKAGE_NAME
    return importlib_resources.files(package_name).joinpath(settings.HUNT_DATA_PACKAGE_CHUNKS)
