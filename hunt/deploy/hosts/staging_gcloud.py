from django_hosts import patterns, host

host_patterns = patterns('',
    # Bonus domain patterns to handle.
    host(r'registration.localhost:8000', 'hunt.deploy.urls.registration', name="registration-dev"),
    host(r'localhost:8000', 'hunt.deploy.urls.site', name="site-dev"),

    # Our real domains.
    host(r'staging.mitmh2022.com', 'hunt.deploy.urls.registration', name='registration', scheme='https://'),
    host(r'staging.starrats.org', 'hunt.deploy.urls.site', name='site-1', scheme='https://'),
    host(r'staging.bookspace.world', 'hunt.deploy.urls.site', name='site-2', scheme='https://'),

    # The host to use by default.
    host(r'staging.mitmh2022.com', 'hunt.deploy.urls.registration', name='default', scheme='https://'),
)
