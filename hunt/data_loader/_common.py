from functools import wraps

# Fallback to the backported importlib.resources for Python < 3.9.
# NB: importlib.resources is available as of Python 3.7, but the `files` function
# was not available until Python 3.9.
try:
    import importlib_resources
except ImportError:
    import importlib.resources as importlib_resources

def allow_compiled_version(fn):
    """
    Decorator which allows the final argument to be replaced with a compiled
    version if it exists.
    """
    @wraps(fn)
    def _wrapped(*args):
        assert len(args)
        other_args = args[:-1]
        last_arg = args[-1]
        for ext in ('.html', '.css'):
            if last_arg.endswith(ext):
                transformed_last_arg = last_arg[:-len(ext)] + '.compiled' + ext
                return fn(*other_args, transformed_last_arg) or fn(*args)
        return fn(*args)
    return _wrapped

