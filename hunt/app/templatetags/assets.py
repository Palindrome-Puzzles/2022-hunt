import urllib.parse

from django import template

from hunt.app.core.assets.refs import get_auxiliary_static_path

register = template.Library()

@register.simple_tag(name='puzz', takes_context=True)
def puzzle_asset(context, resource, solution=False):
    """
    Template tag to refer to puzzle and puzzle solution static assets. This is
    only needed for puzzle subviews.

    Usage:
        `<img src="{% puzz '0.png' }">` to load an image from the puzz
        directory.

        `<img src="{% puzz '0.png' solution=True }">` to load an image from
        the puzz solution directory.
    """
    key = 'spuzz_root' if solution else 'puzz_root'
    root = context[key]
    if not root:
        raise template.TemplateSyntaxError(f'puzz tag could not find key ${key} in context. You probably can\'t use that tag here');
    return urllib.parse.urljoin(root, resource)

@register.simple_tag(name='rd', takes_context=True)
def round_asset(context, resource):
    """
    Template tag to refer to round static assets.

    Usage:
        `<img src="{% rd '0.png' }">` to load an image from the round
        directory.
    """
    key = 'rd_root'
    root = context[key]
    if not root:
        raise template.TemplateSyntaxError(f'rd tag could not find key ${key} in context. You probably can\'t use that tag here');
    return urllib.parse.urljoin(root, resource)


@register.simple_tag(name='aux')
def auxiliary_asset(bucket, resource):
    """
    Template tag to refer to an auxiliary asset by bucket and path.

    Usage:
        `<img src="{% aux 'pen-station' 'images/0.png' }">` to load an image
        from the pen station directory.
    """
    root = get_auxiliary_static_path(bucket)
    return urllib.parse.urljoin(root, resource)
