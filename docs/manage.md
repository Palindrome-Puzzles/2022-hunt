# Management
There are a number of commands and techniques for importing data into the hunt, or changing the state while it is running. As a pre-requisite, please follow the [getting started instructions](../#getting-started) on the repository home page.

## Managing data
To run a command, pass it to Django's `manage.py` script along with a `DJANGO_ENV`. For example, you might run `DJANGO_ENV=dev python manage.py importteams` to re-import teams.

 - `importteams` - imports teams defined in [`/hunt/data/hunt_info/teams.tsv`](/hunt/data/hunt_info/teams.tsv) and creates them or merges them with an existing team with the same username.
     - `--noinput` to avoid confirmations
     - `--change-passwords` to also change the user's password, which will expire any current sessions for the user
 - `importpuzzles` - imports puzzles, rounds, and interactions defined in [`/hunt/data/hunt_info/`](/hunt/data/hunt_info/), and creates or merges them with existing data.
     - `--noinput` to avoid confirmations
 - `checkpuzzles` - runs some consistency checks between puzzles in [`/hunt/data/hunt_info/puzzles.tsv`](/hunt/data/hunt_info/puzzles.tsv) and puzzle bundles in [`/hunt/data/puzzle/`](/hunt/data/puzzle/), and prints any issues
 - `collectpuzzlefiles` - collects all static and puzzle files into the `/static_temp/` directory. It also (optionally) separates gzippable and non-gzippable assets for deployment
     - `--noinput` to avoid confirmations
     - `--gzip-files=false` to skip separating gzippable files
 - `removepuzzlefiles` - deletes the `/static_temp/` directory created by `collectpuzzlefiles`
    - `--noinput` to avoid confirmations
 - `nukecache` - resets the in-memory cache
     - `--noinput` to avoid confirmations
 - `launch` - to advance the [hunt lifecycle](#hunt-lifecycle) by launching a stage
 - `resethuntactivity` - delete most activity by hunt teams (for internal testing)
 - `resethuntlog` - delete system log (for internal testing)

There are other built-in and custom commands as well. `DJANGO_ENV=dev python manage.py` will show a list of all available commands.

## Hunt lifecycle
The hunt proceeded through several stages from launching the registration, launching star rats, opening the hunt, and completing it. For full details, please read [`/hunt/deploy/util.py`](/hunt/deploy/util.py).

The hunt lifecycle can be advanced by using the `launch` Django command as above. For example, to pre-launch the hunt and start releasing puzzles, you can call `DJANGO_ENV=dev python manage.py launch site-prelaunch`.

You can also do it using direct [database access](#database-access). If you do it, you can set the `date_value` column in `spoilr_core_huntsetting` to a specific time that you want the lifecycle to advance.

Note:
 - If using the commands above against Google App Engine, use the `prod_db_only_gcloud` environment instead of `prod_gcloud`, as you won't be able to talk to Redis and the command will crash.
- Some of the commands have side-effects such as unlocking puzzles and sending a notification in [`/hunt/app/core/callbacks.py`](/hunt/app/core/callbacks.py). These are a bit broken -- if you schedule a lifecycle advance in the future using direct database access, then these side-effects won't run. And if you trigger them using a command locally, then they won't be able to reach Redis, so the notifications won't actually be sent. In the future, it'd be better to trigger the side effects independently of advancing the lifecycle.

## Mail merges
A simple mail merge script is defined in [`/hunt/registration/management/commands/`](/hunt/registration/management/commands/).

## HQ
Most administration during a hunt is done through HQ. Please see the tour in the [features section](features.md#hq) for what you can do.

## "Ticking" the hunt
The hunt has behaviour that unlocks at a certain time. For example, actions can be snoozed in HQ, and need to be automatically unsnoozed after a certain amount of time. Or the hunt may be configured to automatically release some puzzles after a few hours to help stuck solving teams.

This is currently implemented using a "tick" URL at <http://localhost:8000/hq/tick>. When visited, it triggers time-based checks and advances the hunt if necessary. It is only accessible to a member of an admin hunt team. Ideally, only one person should be triggering these ticks concurrently to avoid race conditions, but this isn't strictly necessary.

During a hunt, ticking should be automated in some way. An easy way is to write a simple HTML page that auto-refreshes and includes the tick URL in an iframe. If we go this way, then either the wrapper HTML page needs to be deployed to the hunt server as well, or we need to allow cross-origin requests to the tick URL. This needs to be decided when we know more about the hunt unlock strategy.

(We did a quick hack of including the tick URL as an 1x1 iframe on the HQ dashboard.)

## Database access
If you (or someone else) makes changes to the Django models, you'll need to [migrate your database](https://docs.djangoproject.com/en/3.2/topics/migrations/).

If you make model changes:
 1. Run `DJANGO_ENV=dev python manage.py makemigrations` to prepare a migration script inside your repository
 1. (Optional) Inspect the migration script to see if everything looks good
 1. (Optional) Write a [data migration script](https://docs.djangoproject.com/en/3.2/topics/migrations/#data-migrations) if needed and if `makemigrations` didn't handle them already
 1. Run the migration scripts against your database `DJANGO_ENV=dev python manage.py migrate`
 1. Commit the generated migration scripts so that they can be run against other people's local databases, or against our staging/prod databases

If someone else made a model change:
 1. Pull the latest version of the repo to receive their migration script
 1. Run the migration scripts against your database `DJANGO_ENV=dev python manage.py migrate`

In general, we can make database changes pretty freely until very close to hunt, as the only data we care about is in config files. However, it can be annoying to run migrations, etc, so be careful making model changes and give the tech team Discord channel a heads-up that you're doing so.

If you run into a uniqueness constraint while migrating, you may need to flush the whole database. With SQLite, you can just delete the database file. Otherwise, use the `flush` command and re-migrate.
    ```
    DJANGO_ENV=dev python manage.py flush
    DJANGO_ENV=dev python manage.py migrate
    ```

If you're actively developing in these repos, I highly recommend installing the tooling for accessing whatever database you are using. For example, if you're using SQLite, then install the [SQLite Browser](https://sqlitebrowser.org/) to be able to look through the database. There are equivalents for other databases like PostgreSQL too.
