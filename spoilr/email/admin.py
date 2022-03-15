from django.contrib import admin

from .models import IncomingMessage, OutgoingMessage

admin.site.register(IncomingMessage)
admin.site.register(OutgoingMessage)
