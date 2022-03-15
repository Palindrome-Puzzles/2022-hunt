from django import template

register = template.Library()

@register.filter
def times(number):
    return range(number)

@register.filter
def lookup_string(l, i):
    return l[i] if i < len(l) else ''
