from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def book_reports_email():
    return settings.BOOK_REPORTS_EMAIL

@register.simple_tag
def tech_support_email():
    return settings.PUZZLE_TECH_SUPPORT_EMAIL
