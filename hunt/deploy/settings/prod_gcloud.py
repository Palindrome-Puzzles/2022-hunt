from .prod_db_only_gcloud import *
from .common import load_gcloud_secret
from ._redis import get_redis_caches, get_redis_channel_layers

# Note: Keep in sync with the nuke_cache cloud function.
_PROD_REDIS_DB_OFFSET = 1

CACHES = get_redis_caches(_PROD_REDIS_DB_OFFSET)
CHANNEL_LAYERS = get_redis_channel_layers(_PROD_REDIS_DB_OFFSET)

ANYMAIL = {
    'MAILGUN_API_KEY': load_gcloud_secret('mailgun-api-key'),
    "MAILGUN_SENDER_DOMAIN": 'mg.mitmh2022.com',
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
