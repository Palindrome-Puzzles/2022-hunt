import functools

from django.http import HttpResponseForbidden
from django.views.decorators.clickjacking import xframe_options_sameorigin

from spoilr.core.api.decorators import inject_team, require_safe_referrer
from spoilr.hq.models import Handler

def hq(require_handler=False):
    def decorator(view_func):
        @functools.wraps(view_func)
        @xframe_options_sameorigin
        @require_safe_referrer
        @inject_handler(require_handler)
        @inject_team(require_admin=True)
        def wrapped(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def inject_handler(require_handler=False):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped(request, *args, **kwargs):
            handler_id = request.session.get('handler_id')
            request.handler = Handler.objects.filter(id=handler_id).first()
            if require_handler and (not request.handler or not request.handler.sign_in_time):
                return HttpResponseForbidden('Must be signed in as a handler')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
