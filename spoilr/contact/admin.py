from django.contrib import admin

from .models import ContactRequest

class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'create_time', 'team', 'email', 'comment', 'resolved_time')
    list_filter = ('resolved_time', 'team__name')
    search_fields = ['team__name', 'comment']
    ordering = ['create_time']

admin.site.register(ContactRequest,ContactRequestAdmin)
