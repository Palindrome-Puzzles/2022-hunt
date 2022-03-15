import re

from django import template

register = template.Library()

@register.tag
def spacelesser(parser, token):
    """Removes spaces from the HTML output within this tag."""
    nodelist = parser.parse(('endspacelesser',))
    parser.delete_first_token()
    return SpacelesserNode(nodelist)

_WHITESPACE_PATTERN = re.compile(r'\s+')

class SpacelesserNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def replace(self, match):
        # If the spaces match any of the following conditions, they're safe to
        # remove completely.
        #  - the start or end of the document
        #  - after the start of a tag
        #  - before the end of a tag
        if match.start() == 0 or match.string[match.start() - 1] == '>':
            return ''
        if match.end() == len(match.string) or match.string[match.end()] == '<':
            return ''
        # Otherwise, collapse to one space.
        return ' '

    def render(self, context):
        return _WHITESPACE_PATTERN.sub(self.replace, self.nodelist.render(context))
