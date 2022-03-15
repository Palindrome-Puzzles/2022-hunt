import re

# TODO(sahil): Find a better way to avoid rewriting clobbering SVG images (such as in Gears and Arrows).
# For now, just don't rewrite if the URL is '#...' which seems safe enough.

# Adapted from https://github.com/django/django/blob/main/django/contrib/staticfiles/storage.py#L44
_PATTERN_MATCHERS = (
    # CSS url(..) references.
    (
        re.compile(r"""url\(['"]{0,1}\s*(?P<url>[^#]*?)["']{0,1}\)"""),
        """url("%(url)s")""",
    ),
    # CSS @import statements.
    (
         re.compile(r"""@import\s*["']\s*(?P<url>.*?)["']"""),
         """@import url("%(url)s")""",
    ),
    # HTML src="" tags.
    (
        re.compile(r"""src\s*=\s*["'](?P<url>.*?)["']"""),
        """src='%(url)s'""",
    ),
    # HTML href="" tags.
    (
        re.compile(r"""href\s*=\s*["'](?P<url>[^#]*?)["']"""),
        """href='%(url)s'""",
    ),
    # JS import/exports.
    (
        re.compile(r"""(?P<rest>(?:(?:import)|(?:export))\s+(?s:.*?)\s*from\s*)["'](?P<url>.*?)["']"""),
        """%(rest)s'%(url)s'""",
    ),
    (
        re.compile(r"""import\(["'](?P<url>.*?)["']\)"""),
        """import("%(url)s")""",
    ),
    # Passing the static directory to JS code.
    (
        re.compile(r"""\$\$PUZZLE_STATIC_DIRECTORY(?P<url>)\$\$"""),
        """%(url)s""",
    ),
)

def rewrite_relative_paths(source, url_resolver):
    """Rewrites URL references within `source` to the value returned by `url_resolver`."""
    if source:
        for pattern, template in _PATTERN_MATCHERS:
            source = pattern.sub(_get_rewriter(url_resolver, template), source)
    return source

def _get_rewriter(url_resolver, template):
    def handle(match):
        named_matches = match.groupdict()
        raw_url = named_matches['url']

        # Leave template tags as-is.
        if raw_url.startswith('{'):
            return match.group(0)

        resolved_url = url_resolver(raw_url)
        if resolved_url == raw_url:
            return match.group(0)

        named_matches['url'] = resolved_url
        return template % named_matches
    return handle
