from ._prod import *
from .common import load_gcloud_secret

SECRET_KEY = load_gcloud_secret('hunt-secret-key-prod')
PREPEND_WWW = True

ALLOWED_HOSTS = [
    # For local testing.
    'localhost',
    'registration.localhost',

    # Our real domains.
    '.mitmh2022.com',
    '.starrats.org',
    '.bookspace.world',

    # GAE
    '.mitmh-2022.uc.r.appspot.com',
    'mitmh-2022.uc.r.appspot.com',
]
ALLOWED_REDIRECTS = [
    'localhost:8000',
    'registration.localhost:8000',

    'mitmh2022.com',
    'www.mitmh2022.com',
    'starrats.org',
    'www.starrats.org',
    'bookspace.world',
    'www.bookspace.world',
]

DATABASES = {
    # Convert the DB connection string into a database connection dictionary
    # that Django understands.
    'default': env.db_url_config(load_gcloud_secret('hunt-database-url-prod')),
}

# We're running locally - use the Cloud SQL auth proxy.
if HOST_ENV == None or HOST_ENV == 'github':
    DATABASES['default']['HOST'] = '127.0.0.1'
    # The traditional PG port is 5432, but this way, I can run both a local PG
    # and the cloud proxy.
    DATABASES['default']['PORT'] = '5433'

SPOILR_RECEIVE_INCOMING_EMAILS = True
SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS = 'palindrome2022@gmail.com'
ANYMAIL = {
    'MAILGUN_API_KEY': load_gcloud_secret('mailgun-api-key'),
    "MAILGUN_SENDER_DOMAIN": 'mg.mitmh2022.com',
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
