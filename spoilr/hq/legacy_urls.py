from django.urls import path, re_path, include
from django.conf import settings

from . import dashboard
from . import log
from . import updates

urlpatterns = []

urlpatterns += [
    path('', dashboard.dashboard, name='hq'),

    path('log/', log.system_log_view, name='hq_log'),
    re_path('^hint-log/(\d+)?$', log.hint_log_view, name='hq_hintlog'),
    path('updates/', updates.updates_view, name='hq_updates'),
]
