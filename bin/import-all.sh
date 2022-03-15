#!/bin/bash

# Helper script to import hunt data into the database. This is exposed as a script
# so it can be run by GitHub actions.

python manage.py importteams --noinput
python manage.py importpuzzles --noinput
python manage.py nukecache --noinput
