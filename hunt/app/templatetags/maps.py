from django import template

register = template.Library()

@register.simple_tag(name='sticker-css')
def map_sticker_css(sticker_css):
    """
    Template tag to output CSS rules for a sticker.
    """
    if sticker_css:
        return ';'.join(f'{key}:{value}' for key, value in sticker_css.items())
    return ''
