from .staging_db_only_gcloud import *
from .common import load_gcloud_secret
from ._redis import get_redis_caches, get_redis_channel_layers

# Note: Keep in sync with the nuke_cache cloud function.
_STAGING_REDIS_DB_OFFSET = 8

CACHES = get_redis_caches(_STAGING_REDIS_DB_OFFSET)
CHANNEL_LAYERS = get_redis_channel_layers(_STAGING_REDIS_DB_OFFSET)

SPOILR_RECEIVE_INCOMING_EMAILS = True
SPOILR_INCOMING_EMAILS_FORWARDING_ADDRESS = 'palindrome2022.tech@gmail.com'
ANYMAIL = {
    'MAILGUN_API_KEY': load_gcloud_secret('mailgun-api-key'),
    "MAILGUN_SENDER_DOMAIN": 'mg.mitmh2022.com',
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
