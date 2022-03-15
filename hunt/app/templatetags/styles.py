from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def wrap_styles(styles):
    # Note: no need to escape, as this is inside a HTML tag, and trusted.
    # If we do, it breaks attribute selectors and other stuff that uses quotes.
    return mark_safe(f'<style>{styles}</style>' if styles else '')
