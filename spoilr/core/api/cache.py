import functools, hashlib

from django.conf import settings
from django.core.cache import caches

SERVER_CACHE_TIMEOUT_S = 60 * 60;

cache = caches[settings.SPOILR_CACHE_NAME]

def memoized_cache(bucket):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped(*args):
            key = f'memoized:{bucket}:{_hash_args(*args)}'
            return _memoized_cache(view_func, key, *args)
        return wrapped
    return decorator

def clear_memoized_cache(bucket):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped(*args):
            delete_memoized_cache_entry(bucket, *args)
            return view_func(*args)
        return wrapped
    return decorator

def _memoized_cache(result_factory, key, *args, **kwargs):
    result = cache.get(key)
    if not result:
        result = result_factory(*args, **kwargs)
        cache.set(key, result, timeout=SERVER_CACHE_TIMEOUT_S)
    return result

def delete_memoized_cache_entry(bucket, *args):
    key = f'memoized:{bucket}:{_hash_args(*args)}'
    cache.delete(key)

def _hash_args(*args):
    hasher = hashlib.sha256()
    for arg in args:
        str_arg = arg if isinstance(arg, str) else str(arg)
        hasher.update(str_arg.encode('utf-8'))
    return hasher.hexdigest()
