from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .util import ACCESS_TOKEN

def gcloud_warmup_view(request):
    return HttpResponse('ACK', content_type='text/plain')

@xframe_options_sameorigin
def grant_site_access_view(request):
    assert settings.HUNT_WEBSITE_ACCESS_TOKEN
    response = HttpResponse('Access granted')
    response.set_cookie(ACCESS_TOKEN, settings.HUNT_WEBSITE_ACCESS_TOKEN)
    return response
