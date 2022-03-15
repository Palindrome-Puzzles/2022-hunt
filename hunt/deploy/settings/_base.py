"""
Base Django settings for the 2022 MIT Mystery Hunt server. This should be
extended by environment-specific settings files.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/.

For a pre-deploymnet checklist, see
https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/.
"""

import environ, os
from .common import BASE_PATH, HUNT_CACHE_NAME, HQ_CACHE_NAME, SPOILR_CACHE_NAME, SESSION_CACHE_NAME

env = environ.Env(
    GAE_SERVICE=(str, None),
    ON_HEROKU=(str, None),
    GITHUB_WORKFLOW=(str, None),
)
env.read_env(os.path.join(BASE_PATH, '.env'))

# Section 1: Django and app core settings. Environment-specific settings should
# probably override these.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# The Python logging level https://docs.python.org/3/library/logging.html#levels.
ROOT_LOG_LEVEL = 'WARNING'

if env('GAE_SERVICE'):
    HOST_ENV = 'gcloud'
elif env('ON_HEROKU'):
    HOST_ENV = 'heroku'
elif env('GITHUB_WORKFLOW'):
    HOST_ENV = 'github'
else:
    HOST_ENV = None

# Section 2: Hunt configuration.

# Configuration for puzzle and round data. Make sure the MANIFEST.in in the
# corresponding hunt directory matches these directories.
HUNT_DATA_PACKAGE_NAME = 'hunt.data'
HUNT_DATA_PACKAGE_PUZZLE_DATA = 'puzzle/'
HUNT_DATA_PACKAGE_ROUND_DATA = 'round/'
HUNT_DATA_PACKAGE_HUNT_INFO_DATA = 'hunt_info/'
HUNT_DATA_PACKAGE_AUXILIARY_DATA = 'auxiliary/'
HUNT_DATA_PACKAGE_CHUNKS = 'chunks/'

# Whether to serve puzzle assets (i.e. images/scripts used in a puzzle or round)
# statically (True) or through a Django view (False).
#
# Serving statically is more performant. However, it requires a separate deploy
# step to generate the static assets. It should be used in production.
#
# Serving through a Django view doesn't require a separate deployment step, so
# is useful for development and puzzle testing.
HUNT_ASSETS_SERVE_STATICALLY = True
# Directory within static files for statically deployed assets.
HUNT_ASSETS_STATIC_PREFIX = 'puzzle_files/'
# Directory where we temporarily collect statically deployed assets.
HUNT_ASSETS_TEMP_FOLDER = os.path.join(BASE_PATH, 'static_temp/')

# Whether the hunt no longer allows team login.
HUNT_LOGIN_ALLOWED = False

# The name of the team for public access to the hunt, or None if no public
# access is allowed.
HUNT_PUBLIC_TEAM_NAME = None

# Whether to enable sample puzzles and rounds.
HUNT_LOAD_SAMPLE_ROUND = False

# Whether to enable the puzzleviewer utility.
HUNT_PUZZLEVIEWER_ENABLED = False

# Magic token to include as a GET param, to access the website, or None if no
# magic token is needed. This can be used to gate access to staging websites.
HUNT_WEBSITE_ACCESS_TOKEN = None

# Whether to still import puzzles that are missing assets and just use placeholder
# metadata.
HUNT_SHOULD_STUB_MISSING_PUZZLES = False

# Whether to enable caching on the server and conditional gets from the browser.
HUNT_ENABLE_CACHING = True
HUNT_ENABLE_FILE_CACHING = True

# For local development apps that allow dynamic refreshing of CSS.
HUNT_SERVE_CSS_FROM_FILE = False

# Whether to enable the Django admin portal.
SPOILR_ENABLE_DJANGO_ADMIN = False
SPOILR_ENABLE_DJANGO_ADMIN_DOCS = False

# Answer that can be used by admin teams to automatically use the correct answer
# when submitting an answer to a puzzle.
SPOILR_ADMIN_MAGIC_ANSWER = 'ANSWER'

# How many open hints are allowed at once.
HUNT_OPEN_HINTS_QUOTA = 1
HUNT_OPEN_HINTS_EXPANDED_QUOTA = 2
# How many teams need to solve a puzzle before hints are released.
HUNT_SOLVES_BEFORE_HINTS_RELEASED = 30
HUNT_RD3_SOLVES_BEFORE_HINTS_RELEASED = 10

HUNT_ROUND_BREAKGLASS_UNLOCKS_ENABLED = False

HUNT_REGISTRATION_CLOSED = False

# Section 3: Application definition. This will be fixed across all environments.

ASGI_APPLICATION = 'hunt.deploy.asgi.application'
WSGI_APPLICATION = 'hunt.deploy.wsgi.application'

# Should never be used, as we have a default host.
ROOT_URLCONF = 'hunt.deploy.urls.site'

ROOT_HOSTCONF = f'hunt.deploy.hosts.{env("DJANGO_ENV")}'
DEFAULT_HOST = 'default'

INSTALLED_APPS = [
    # Django official apps.
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Other 3p apps.
    'anymail',
    'channels',
    'django_bleach',
    'django_hosts',

    # MIT Mystery Hunt apps.
    'hunt.app',
    'hunt.data',
    'hunt.deploy',
    'hunt.registration',
    'hunt.puzzleviewer',

    'spoilr.contact',
    'spoilr.core',
    'spoilr.email',
    'spoilr.events',
    'spoilr.hints',
    'spoilr.hq',
    'spoilr.interaction',
    'spoilr.progress',
]

MIDDLEWARE = [
    # Default middleware suggested by Django, along with
    # - whitenoise
    # - django_hosts
    # - conditional get
    #
    # and without
    # - clickjacking protection.
    'django.middleware.security.SecurityMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
    'ratelimit.middleware.RatelimitMiddleware'
]

# Load templates from each installed app dir automatically.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            # Add context processors to automatically inject some variables into
            # the template context.
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Section 4: Databases, caches, sessions, and channels. These MUST be changed for
# production.

# Specify a default auto field type for auto-generated primary keys. Use
# BigAutoField because this is a greenfield project so why not.
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_PATH, 'db.sqlite3'),
    }
}

# https://docs.djangoproject.com/en/3.2/ref/settings/#caches
CACHES = {
    HUNT_CACHE_NAME: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    },
    HQ_CACHE_NAME: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    SPOILR_CACHE_NAME: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    SESSION_CACHE_NAME: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

# https://channels.readthedocs.io/en/stable/topics/channel_layers.html#configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

SESSION_CACHE_ALIAS = SESSION_CACHE_NAME
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


# Section 5: Static files (CSS, Javascript, images, fonts, etc) configuration.
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# URL prefix when serving static files.
STATIC_URL = '/static/'

# Where static files are stored when running the `collectstatic` method, and
# where Django will look when serving static files.
STATIC_ROOT = os.path.join(BASE_PATH, "static")

# Extra directories to look for static files, other than the static/ sub-directory
# of each installed app.
STATICFILES_DIRS = []


# Section 6: Security and authentication.

# Use the spoilr user model.
AUTH_USER_MODEL = 'spoilr_core.User'

LOGIN_URL = 'login'

# NB: Disable clickjacking projection by default. Plenty of solving teams use an
# iframed hunt website to collaboratively solve. Instead, we need to ensure
# sensitive actions (like submitting an answer) are appropriately guarded.
# https://docs.djangoproject.com/en/3.2/ref/clickjacking/.

# Password validators for users. Note: this only affects the user used to access
# HQ and the admin portals (if enabled). It's unrelated to the login flow used
# by teams.
# https://docs.djangoproject.com/en/3.2/topics/auth/passwords/#password-validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# https://docs.djangoproject.com/en/3.2/ref/middleware/#django.middleware.security.SecurityMiddleware
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Default cookie policies.
#
# Secure controls whether the cookie is sent on HTTP requests, or just for HTTPS
# requests. It should only be False for dev environments
#
# Samesite controls whether cookies should be sent when the hunt website is
# loaded by or navigated to by a third party.
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
#
# The settings below are the same as Django defaults, except with each cookie
# being secure-only. Be careful changing them to other values in production.

# We're allowing session and CSRF cookies to be cross-origin so that the hunt
# can be embedded in an iframe. We need to be careful to guard against
# clickjacking and verify referrers as a result.
LANGUAGE_COOKIE_SAMESITE = 'None'
LANGUAGE_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True


# Section 7: Internationalization.
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# Note: we don't offer a way for users to change their locale, and we haven't
# translated any content, so the only thing these do is ensure dates and numbers
# are shown in the right format.
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = True

# Ensure datetimes are timezone aware. Treat all datetimes entered into forms,
# and display all datetimes in the specified timezone.
USE_TZ = True
TIME_ZONE = 'America/New_York'


# Section 8: 3p Integrations.
DEFAULT_FROM_EMAIL = None
SERVER_EMAIL = None
HUNT_SUBMISSIONS_EMAIL = None
HUNT_BOOKREPORT_EMAIL = None # This isn't used
SPOILR_HINTS_FROM_EMAIL = None
STORY_FROM_EMAIL = None
BOOK_REPORTS_EMAIL = None

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SPOILR_HQ_DEFAULT_FROM_EMAIL = None

SPOILR_RECEIVE_INCOMING_EMAILS = False
SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS = None
# For some incoming emails, we can't pretend to be sending email from the domain
# due to something called DMARC. But basically, that's to prevent us pretending
# to be Google and stealing account info. For those, we have to fallback to
# using a different sender address.
SPOILR_RELAY_IMPERSONATE_BLACKLIST = {
    '@google': 'google',
    '@yahoo': 'yahoo',
    '@aol': 'aol',
    '@btinternet': 'btinternet',
    '@qq.com': 'qq',
    '@aveva.com': 'aveva',
    '@postmarkapp.com': 'postmarkapp',
    '@s1.com': 'amazon',
    '@blogspot': 'blogspot',
}

BLEACH_ALLOWED_TAGS  = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'strong', 'u', 'ul']
RATELIMIT_VIEW = 'hunt.app.views.top_views.ratelimited_error_view'

PUZZLE_TECH_SUPPORT_EMAIL = None

# TODO(sahil): Add discord config.

