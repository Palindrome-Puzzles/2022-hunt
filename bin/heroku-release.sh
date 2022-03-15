#!/bin/bash

# Pre-release script for Heroku, to migrate Django models automatically.

python manage.py migrate

# NB: This probably isn't needed as Heroku is only doing in-memory caching, and
# y'know, we just did a release. However, let's leave it here so stuff works if
# we ever add a shared cache server.
python manage.py nukecache --noinput
