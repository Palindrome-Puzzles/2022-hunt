from ._prod import *

SECRET_KEY = env('SECRET_KEY')
# Heroku internally uses http traffic, so use the magic header to indicate if
# traffic was HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# TODO(sahil): We'd like to use prepend www but it breaks heroku which doesn't
# allow www to be prefixed on their sub-domains.
PREPEND_WWW = False

ALLOWED_HOSTS = [
    # For local testing.
    'localhost',
    'registration.localhost',

    # Our real domains.
    '.mitmh2022.com',
    '.starrats.org',
    '.bookspace.world',
    '.palindrome-hunt-prod.herokuapp.com',
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
    'palindrome-hunt-prod.herokuapp.com',
]

DATABASES = {
    # Automatically grabs the database connection string from `os.environ['DATABASE_URL']`
    # and converts it to a database connection dictionary that Django understands.
    'default': env.db_url(),
}

ANYMAIL = {
    'MAILGUN_API_KEY': env('MAILGUN_API_KEY'),
    "MAILGUN_SENDER_DOMAIN": 'mg.mitmh2022.com',
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

SPOILR_RECEIVE_INCOMING_EMAILS = True
SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS = 'palindrome2022@gmail.com'

# TODO(sahil): Add a cache and channel layer (redis).
