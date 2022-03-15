from ._base import *
from .common import BASE_PATH

DEBUG = True
SECRET_KEY = '123dev456'
ROOT_LOG_LEVEL = 'INFO'

ALLOWED_HOSTS = [
    'localhost',
    'bookspace.localhost',
    'registration.localhost',
]
ALLOWED_REDIRECTS = [
    'localhost:8000',
    'bookspace.localhost:8000',
    'registration.localhost:8000',
]

# Just use a local sqlite database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_PATH, 'db.sqlite3'),
    }
}

# Allow cookies over http so we can develop locally.
LANGUAGE_COOKIE_SAMESITE = 'Lax'
LANGUAGE_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False

# Turn on the Django admin panel.
SPOILR_ENABLE_DJANGO_ADMIN = True
SPOILR_ENABLE_DJANGO_ADMIN_DOCS = True

# In development, allow Django to serve assets dynamically.
HUNT_ASSETS_SERVE_STATICALLY = False

HUNT_LOAD_SAMPLE_ROUND = True
HUNT_PUZZLEVIEWER_ENABLED = True
HUNT_SHOULD_STUB_MISSING_PUZZLES = True

# Make development easy by not caching anything (including local files, but
# that's redundant).
HUNT_ENABLE_CACHING = False
HUNT_ENABLE_FILE_CACHING = False

SPOILR_HQ_DEFAULT_FROM_EMAIL = 'hq@example.com'
SPOILR_HINTS_FROM_EMAIL = 'hints@example.com'
STORY_FROM_EMAIL = 'story@example.com'
BOOK_REPORTS_EMAIL = 'bookreports@example.com'
EMOJI_ART_EMAIL = 'emojiart@example.com'

HUNT_SOLVES_BEFORE_HINTS_RELEASED = 3
HUNT_RD3_SOLVES_BEFORE_HINTS_RELEASED = 1
HUNT_ROUND_BREAKGLASS_UNLOCKS_ENABLED = True

HUNT_PUBLIC_TEAM_NAME = 'public'
HUNT_LOGIN_ALLOWED = True
