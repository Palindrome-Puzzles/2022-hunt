from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import escape

def XHttpResponse(d):
    """Helper method to safely indicate an internal error."""
    return HttpResponse(escape(d))
