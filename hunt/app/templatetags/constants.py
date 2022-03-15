from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def book_reports_email():
    return settings.BOOK_REPORTS_EMAIL
