from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def is_non_archive():
    return not settings.HUNT_ARCHIVE_MODE

@register.simple_tag
def archivable_font(google_fonts_family, local_declaraction):
    return (
        static(f'fonts/{local_declaraction}.css')
        if settings.HUNT_ARCHIVE_MODE
        else f'https://fonts.googleapis.com/css2?family={google_fonts_family}&display=swap')
