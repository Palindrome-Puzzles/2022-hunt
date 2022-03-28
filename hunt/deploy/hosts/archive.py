from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'127.0.0.1:8000', 'hunt.deploy.urls.unified', name='registration'),
    host(r'127.0.0.1:8000', 'hunt.deploy.urls.unified', name='site-1'),
    host(r'127.0.0.1:8000', 'hunt.deploy.urls.unified', name='site-2'),
    host(r'127.0.0.1:8000', 'hunt.deploy.urls.unified', name='default'),
)
