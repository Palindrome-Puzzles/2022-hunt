from django.contrib import admin

from .models import Event, EventParticipant

admin.site.register(Event)
admin.site.register(EventParticipant)
