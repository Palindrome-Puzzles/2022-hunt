from django.conf import settings

from ._common import importlib_resources

def get_auxiliary_data_text(*path):
    """
    Returns the content of a auxiliary file as text, or None if the file does
    not exist.
    """
    path = get_all_auxiliary_files().joinpath(*path)
    return path.read_text(encoding='utf8') if path.exists() else None

def get_auxiliary_data_file(*path):
    """
    Returns the content of a auxiliary file as bytes, or None if the file does
    not exist.
    """
    path = get_all_auxiliary_files().joinpath(*path)
    return path.open('rb') if path.exists() else None

def get_all_auxiliary_files():
    package_name = settings.HUNT_DATA_PACKAGE_NAME
    return importlib_resources.files(package_name).joinpath(settings.HUNT_DATA_PACKAGE_AUXILIARY_DATA)
