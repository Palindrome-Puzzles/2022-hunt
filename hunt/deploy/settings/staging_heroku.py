from ._staging import *

SECRET_KEY = env('SECRET_KEY')
# Heroku internally uses http traffic, so use the magic header to indicate if
# traffic was HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
    # For local testing.
    'localhost',
    'registration.localhost',

    # Our real domains.
    'palindrome-hunt-staging.herokuapp.com',
]
ALLOWED_REDIRECTS = [
    'localhost:8000',
    'registration.localhost:8000',

    'palindrome-hunt-staging.herokuapp.com',
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

# TODO(sahil): Add a cache and channel layer (redis).
