# Deployment configuration
This directory defines settings and configuration for running the 2022 Hunt Server against standard environments.

## Using your own settings
The Django environment is used to select the settings file to use. If you need to change your local settings without committing them, then:
 - Create a file called `local.py` here and extend from `_base.py` (see `dev.py`).
 - Create a file called `local.py` in `hunt.deploy.hosts` and set up the URL mapping for the local environment (see `dev.py` as a template). The chosen hosts should also be added to `ALLOWED_HOSTS` in the env-specific settings file.
 - Use `DJANGO_ENV=local` when running the server.

## Staging environment
This is an environment for internal testing with the team. It's currently set up to deploy to Heroku.

When deploying, ensure the following environment variables are available (either
in `.env` or as an environment secret).
 - `DATABASE_URL`
 - `PORT`
 - `SECRET_KEY`

If you want to test the Heroku instance locally, you can do the following:
 - Install the `heroku` CLI.
 - Initialize the variables above in `.env`.
    - If you use a new database, make sure you run the following commands: `migrate`, `createsuperuser`, `importteams`, and `importpuzzles`. See the [top-level documentation](../../../#initial-setup) for more details.
 - Run `DJANGO_ENV=staging heroku local release` to simulate the release phase (deploy static files).
 - Run `DJANGO_ENV=staging heroku local`

> **Note**: On Windows, the `Procfile` needs to be edited to change `$PORT` to `%PORT%` because of environment variable interpolation differences.

## Production-ready settings
When running in staging/production, you MUST do the following.
 - Use a securely generated secret for `SECRET_KEY` and load it from the environment. It should be set in the environment by some secret management service if available. The secret should **not** be checked into the repository.
    `SECRET_KEY = os.environ['DJANGO_SECRET_KEY']`
 - Set `DEBUG` to False.
 - Set `ALLOWED_HOSTS` to only the hosts where the instance is running.
 - Configure a production-ready database. The default in `_base.py` (SQLite) should not be used.
 - Configure a production-ready cache. The default in `_base.py` (local-memory) should not be used.
 - Configure a production-ready channel layer. The default in `_base.py` (in-memory) should not be used.
 - Configure the server to serve static assets directly. Serving using Django or Whitenoise is relatively inefficient compared to a proper CDN.

## Settings recipes
A guide to customizing the settings to work with different environments.

### Databases
Use a local sqlite database.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_PATH, 'db.sqlite3'),
    }
}
```

Use a hosted database like MySQL.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '???',
        'USER': '???',
        'PASSWORD': '???',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

Use a database with a connection string as provided by services like Google CloudSQL or Heroku.
```
import dj_database_url

DATABASES = {
    # Automatically grabs the database connection string from `os.environ['DATABASE_URL']`
    # and converts it to a database connection dictionary that Django understands.
    'default': dj_database_url.config()
}
```

If testing locally against a a Google CloudSQL database, you will need to use an authentication proxy.

First follow the [instructions](https://cloud.google.com/python/django/appengine#run-locally) to download and start the proxy.

Then update the settings to [point to the proxy](https://cloud.google.com/python/django/appengine#database_connection).

### Channels
[Channels](https://channels.readthedocs.io/en/stable/introduction.html) allow Django to support asynchronous protocols like WebSockets. These protocols are stateful so we need a communication layer between different instances of the application. Channel layers allow you to set this up.

As such, any production build MUST set up some channel layers to have WebSockets work reliably.

Using Redis to store channel layers.
```
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    'address': ('<REDIS_HOST>', 6379),
                    'db': 2,
                },
            ],
            "capacity": 1000,
            "expiry": 10,
        },
    }
}
```

### Caches
We use [caches](https://docs.djangoproject.com/en/3.2/topics/cache/) to avoid re-computing expensive data. For example, a team's context including the puzzles they've solved, etc could be cached until they solve or unlock a puzzle somehow.

If we want caches to be shared across different instances of the application, we need a dedicated server. We can use [django-redis](https://github.com/jazzband/django-redis) to reuse the Redis server spun up to support [channel layers](#channels).

```
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://<REDIS_HOST>:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

**Warning**: Make sure to use a different Redis _database_ compared to the channel layer, to avoid collisions.
