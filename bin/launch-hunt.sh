#!/bin/bash

# Helper script to launch the hunt and the registration website. This is exposed
# as a script so it can be run by GitHub actions, for staging environments.

python manage.py launch registration
python manage.py launch rd0
python manage.py launch rd0-released
python manage.py launch site-prelaunch
python manage.py launch hunt
