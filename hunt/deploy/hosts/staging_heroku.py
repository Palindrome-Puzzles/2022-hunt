from django_hosts import patterns, host

host_patterns = patterns('',
    # Bonus domain patterns to handle.
    host(r'registration.localhost:8000', 'hunt.deploy.urls.registration', name="registration-dev"),
    host(r'localhost:8000', 'hunt.deploy.urls.site', name="site-dev"),

    # Our real domains.
    host(r'palindrome-hunt-staging.herokuapp.com', 'hunt.deploy.urls.unified', name='registration', scheme='https://'),
    host(r'palindrome-hunt-staging.herokuapp.com', 'hunt.deploy.urls.unified', name='site-1', scheme='https://'),
    host(r'palindrome-hunt-staging.herokuapp.com', 'hunt.deploy.urls.unified', name='site-2', scheme='https://'),

    # The host to use by default.
    host(r'palindrome-hunt-staging.herokuapp.com', 'hunt.deploy.urls.unified', name='default', scheme='https://'),
)
