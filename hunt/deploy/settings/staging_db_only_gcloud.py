from ._staging import *
from .common import load_gcloud_secret

SECRET_KEY = load_gcloud_secret('hunt-secret-key-staging')

ALLOWED_HOSTS = [
    # For local testing.
    'localhost',
    'registration.localhost',

    # Our real domains.
    '.staging.mitmh2022.com',
    '.staging.starrats.org',
    '.staging.bookspace.world',

    # GAE
    '.mitmh-2022.uc.r.appspot.com',
]
ALLOWED_REDIRECTS = [
    'localhost:8000',
    'registration.localhost:8000',

    'staging.mitmh2022.com',
    'staging.starrats.org',
    'staging.bookspace.world',
]

DATABASES = {
    # Convert the DB connection string into a database connection dictionary
    # that Django understands.
    'default': env.db_url_config(load_gcloud_secret('hunt-database-url-staging')),
}

# We're running locally - use the Cloud SQL auth proxy.
if HOST_ENV == None or HOST_ENV == 'github':
    DATABASES['default']['HOST'] = '127.0.0.1'
    # The traditional PG port is 5432, but this way, I can run both a local PG
    # and the cloud proxy.
    DATABASES['default']['PORT'] = '5433'
