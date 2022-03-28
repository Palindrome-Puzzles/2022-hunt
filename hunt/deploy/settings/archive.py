from .dev import *

DEBUG = False
SECRET_KEY = 'archive'

ALLOWED_HOSTS = [
    '127.0.0.1',
]
ALLOWED_REDIRECTS = [
    '127.0.0.1:8000',
]

HUNT_LOGIN_ALLOWED = False
HUNT_FORCE_PUBLIC_TEAM = True
HUNT_ARCHIVE_MODE = True
