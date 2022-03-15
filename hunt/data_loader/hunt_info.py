from django.conf import settings
from ._common import importlib_resources

def get_hunt_info(*path):
    """
    Returns a traversable hunt info file, or None if the file does not exist.
    """
    path = _get_hunt_info(*path)
    return path if path.exists() else None

def _get_hunt_info(*path):
    package_name = settings.HUNT_DATA_PACKAGE_NAME
    hunt_info_data_prefix = settings.HUNT_DATA_PACKAGE_HUNT_INFO_DATA

    return importlib_resources.files(package_name).joinpath(hunt_info_data_prefix, *path)
