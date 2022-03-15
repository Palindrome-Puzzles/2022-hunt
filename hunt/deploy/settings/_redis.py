from .common import load_gcloud_secret, HUNT_CACHE_NAME, HQ_CACHE_NAME, SPOILR_CACHE_NAME, SESSION_CACHE_NAME

def get_redis_caches(offset):
    # Note: Keep the number of caches and indexing in sync with the nuke_cache
    # cloud function.
    redis_host = load_gcloud_secret("redis-host")
    return {
        name: {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://{redis_host}:6379/{offset + 1 + index}',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        } for index, name in enumerate((HUNT_CACHE_NAME, HQ_CACHE_NAME, SPOILR_CACHE_NAME, SESSION_CACHE_NAME))
    }

def get_redis_channel_layers(offset):
    return {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [{'address':(load_gcloud_secret('redis-host'), 6379), 'db': offset}],
                "capacity": 1000,
                "expiry": 10,
            },
        }
    }
