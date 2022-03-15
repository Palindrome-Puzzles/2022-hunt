from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'registration.localhost:8000', 'hunt.deploy.urls.registration', name='registration'),
    host(r'localhost:8000', 'hunt.deploy.urls.site', name='site-1'),
    host(r'bookspace.localhost:8000', 'hunt.deploy.urls.site', name='site-2'),
    host(r'localhost:8000', 'hunt.deploy.urls.registration', name='default'),
)
