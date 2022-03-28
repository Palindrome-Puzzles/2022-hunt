# Deploying the hunt
This page describes how to configure and deploy your own copy of the hunt. As a pre-requisite, please follow the [getting started instructions](../#getting-started) on the repository home page.

## Environments
The hunt website uses a declarative config to control things like:
 - The domain(s) it runs on
 - What database to use
 - Configuring features like [caching](features.md#caching), [Puzzleviewer](features.md#puzzleviewer), hints configuration, how to serve puzzle assets
 - and more...

Bundles of configuration are referred to as an "environment", and the name of the environment is passed as the `DJANGO_ENV` environment variable when running the server.

An environment's config is split across two files. For the `dev` environment, the files are:
 - [`hunt/deploy/settings/dev.py`](/hunt/deploy/settings/dev.py) for Django settings
 - [`hunt/deploy/hosts/dev.py`](/hunt/deploy/hosts/dev.py) for configuring how URLs are mapped for each domain name in the environment

To learn about the available settings, you can read [`_base.py`](/hunt/deploy/settings/_base.py) which documents and sets defaults for settings defined in this repository. You can also use [Django's built-in settings](https://docs.djangoproject.com/en/3.2/ref/settings/) (or settings for third-party Django apps).

URLs are configured as per the [django-hosts](https://django-hosts.readthedocs.io/en/latest/) package -- you can see the existing configs as examples.

Each host config rule requires a unique name. The following host config names have special meaning:
 - `site-1`: The domain to use when redirecting to the Star Rats site content.
 - `site-2`: The domain to use when redirecting to the Bookspace site content.
 - `registration`: The domain to use when redirecting to the registration site.
 - `default`: The domain to assume we're on if we can't recognize the current domain per this config.

All of the above names **must** be present in your hosts config file. Any other names for host config rules are arbitrary and optional.

The second argument for each host config rule refers to a module with a Django URL configuration. These probably don't need to be changed - you just need to pick the right one when writing a host config rule.
 - [`hunt.deploy.urls.unified`](/hunt/deploy/urls/unified.py): Serve all URLs at this domain. (Registration URLs are prefixed with a `/registration/` path.)
 - [`hunt.deploy.urls.site`](/hunt/deploy/urls/site.py): Serve only the URLs for the hunt website.
 - [`hunt.deploy.urls.registration`](/hunt/deploy/urls/registration.py): Serve only the URLs for the registration website.

### Existing environments
The existing environments are:
 - `dev`: for development
 - `staging_gcloud` and `prod_gcloud`: for Google App Engine
 - `staging_heroku` and `prod_heroku`: for Heroku
 - `archive`: for [archiving the hunt](archive.md)

(The [tech stack](tech-stack.md) documentation talks about why we have both.)

There are also pseudo-environments for [running Django commands](manage.md) or CI/CD. These pseudo-environments are:
 - `staging_deploy` and `prod_deploy`: Used for deploying assets to the Google Cloud Storage CDN (for use in both Google App Engine and Heroku). This has fewer dependencies (no database or Redis), so that it runs faster on Github Actions reducing cost.
 - `staging_db_only_gcloud` and `prod_db_only_gcloud`: So we can run commands either locally or in Github Actions, without connecting to [Memorystore (Redis)](https://chamikakasun.medium.com/how-to-connect-redis-instance-from-your-gae-5054c90ad031), which can't (easily) be done outside Google's network.

### Local environment
If making local changes to configurations, I recommend making a new environment called `local`, and extending it from the `dev` environment by including `from .dev import *` at the start of the settings files. `.gitignore` is already set up to ignore changes to that file, so it's ideal for not letting your changes affect other collaborators.

Then use `DJANGO_ENV=local` when running the hunt server or any Django commands.


## Your own version of the hunt
If you want to deploy your own shareable version of the hunt, you can follow these instructions. It describes the simplest version running on Heroku on their free subdomains. You can see details of our more complex setup in the [tech stack](tech-stack.md) documentation.

The following instructions assume you're starting afresh with none of the 2022 puzzles. (In other words, you've deleted most of [`hunt/data/puzzle/`](/hunt/data/puzzle/) and [`hunt/data/round/`](/hunt/data/round/).) Otherwise, you'll exceed the Heroku maximum "slug" size of 500 MB and deployment will fail.

If this is not true, tweak the instructions as described in the [appendix at the end of these steps](#appendix-exceeding-herokus-slug-size).

 1. Sign up for a free Heroku account, and provision an app and a Postgres database. [The quickstart guide](https://devcenter.heroku.com/articles/getting-started-with-python) will be helpful.
 1. Make your own copy of this repo. Either:
     - Make a public fork (and don't use LFS),
     - Make a public copy that isn't a fork (if you want use LFS),
     - Make a private fork and generate a [Personal Access Token](https://github.com/settings/tokens) for the repo.
 1. Tweak [`_prod.py`](/hunt/deploy/settings/_prod.py) to set up the hunt as you'd like it. For example, you probably want to:
     - Open registration (`HUNT_REGISTRATION_CLOSED`)
     - Allow login (`HUNT_LOGIN_ALLOWED`)
     - Disable serving assets from a CDN (`HUNT_ASSETS_SERVE_STATICALLY`) for a simpler deployment and set `STATIC_URL = '/static/'`
     - Make puzzle files available for static serving - set `STATICFILES_DIRS = [HUNT_ASSETS_TEMP_FOLDER + 'not-gzip/']`
 1. Tweak [`prod_heroku.py`](/hunt/deploy/settings/prod_heroku.py) settings:
     - Change `ALLOWED_HOSTS` and `ALLOWED_REDIRECTS`. These control which domains the app can serve on, and can redirect to during [SSO authentication](features.md#authentication). Replace `palindrome-hunt-prod.herokuapp.com` with the app URL you created in the first step.
     - Optionally delete the "real domains" used during the 2022 hunt.
     - Delete the `ANYMAIL` and `EMAIL_BACKEND` settings (unless you set up a mailgun API key and [add it as an environment variable](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true#define-config-vars) to Heroku).
 1. Tweak [`prod_heroku.py`](/hunt/deploy/hosts/prod_heroku.py) hosts. Copy the contents of [`staging_heroku.py`](/hunt/deploy/settings/staging_heroku.py) into your `prod_heroku.py` file, and update `palindrome-hunt-staging.herokuapp.com` with the app URL you created in the first step.
     - > **Tip**: If you're using your own non-Heroku domain, then keep [`prod_heroku.py`](/hunt/deploy/settings/prod_heroku.py) as a starting point.
 1. (If using Git LFS) Add the [Git LFS buildpack](https://elements.heroku.com/buildpacks/raxod502/heroku-buildpack-git-lfs) so LFS content can be loaded by heroku.
    ```
    heroku buildpacks:add https://github.com/raxod502/heroku-buildpack-git-lfs
    ```
 1. Also add the node.js buildpack, so that it automatically builds puzzle content.
    ```
    heroku buildpacks:add --index 1 heroku/nodejs
    ```
 1. Add a `post_compile` hook to Heroku's buildpacks. Use this to re-collect static files, as otherwise, when the Heroku dyno is restarted, the filesystem is erased and static file serving will fail. Create a file called `bin/post_compile` and set the following contents:
    ```
    #!/usr/bin/env bash

    # Deploy static files whenever the dyno is compiled.
    # This post_compile hook is run by heroku-buildpack-python.
    # https://www.codementor.io/@samueljames/a-workaround-heroku-s-ephemeral-file-system-e6w341zqa

    echo "Post-compile hook: deploy static"

    MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
    MANAGE_FILE=${MANAGE_FILE:2}
    python $MANAGE_FILE collectpuzzlefiles --noinput --gzip-files=false
    ```
 1. In Heroku, set the following config vars.
     - `DJANGO_ENV` to `prod_heroku`
     - `ON_HEROKU` to `1`
     - `SECRET_KEY` to some securely generated random value
     - (If using Git LFS) `BUILDPACK_GIT_LFS_REPO` to the URL of your forked repo including the Personal Access Token from the second step (if the repo is private).
        - Example: `https://<personal-access-token>@github.com/<your-user>/2022-hunt`
 1. Push to Heroku and if using LFS, include the `--no-verify` flag.
    ```
    git push heroku main --no-verify
    ```
 1. Import teams and puzzles, launch the hunt.
    ```
    heroku run bash
    ```
    and then in the [one-off dyno](https://devcenter.heroku.com/articles/one-off-dynos#an-example-one-off-dyno):
    ```
    python manage.py importteams
    python manage.py importpuzzles

    python manage.py launch registration
    python manage.py launch rd0
    python manage.py launch rd0-released
    python manage.py launch hunt
    ```

After this, you can follow the [management guide](manage.md) to administer the hunt. For Django commands, either run them in a [one-off dyno](https://devcenter.heroku.com/articles/one-off-dynos#an-example-one-off-dyno) as above, or set up a `.env` file in the root directory and set the following keys to the same values as the environment variables configured in Heroku. Then you'll be able to run commands in a local terminal using `DJANGO_ENV=prod_heroku python manage.py ...`.
 - `SECRET_KEY=...`
 - `DATABASE_URL=...`

### Appendix: Exceeding Heroku's slug size
If you exceed Heroku's slug size, then the easiest solution is to host your static assets elsewhere. One way to do that is to perform the following additional steps.
 - Set up `.env` as discussed at the end of the above section with the same `SECRET_KEY` as your Heroku instance.
 - Sign up for Google Cloud and optionally set up billing.
 - Set up the Google Cloud `gsutil` command line utility.
 - Create a new Google Cloud Storage bucket, or choose the default bucket with a free tier. Ensure files are all [publicly accessible in the bucket](https://cloud.google.com/storage/docs/access-control/making-data-public#buckets) (and use the `roles/storage.legacyObjectReader` role to avoid users being able to browse files).
 - Locally, run `DJANGO_ENV=prod_heroku python manage.py collectpuzzlefiles --gzip-files=false` to gather all puzzle files in the `/static_temp/` sub-directory.
 - Run the following command to deploy all your assets to Google Cloud Storage `gsutil -m rsync -c -d -R static_temp/not-gzip/ gs://CLOUD_BUCKET_NAME/static/` (after replacing the `CLOUD_BUCKET_NAME`).
 - Delete the `bin/post_compile` file added above, as it is no longer needed.
 - Set the following settings:
    - `STATIC_URL = 'https://storage.googleapis.com/CLOUD_BUCKET_NAME/static/'`
    - `HUNT_ASSETS_SERVE_STATICALLY = True`
    - `STATICFILES_DIRS = []`
 - Re-deploy to heroku.

Then you also need to setup CORS for the Google Cloud bucket, so that scripts can be loaded from the Google Cloud domain, and run as part of your hunt website. To do this:
 1. Modify the configs in [`/hunt/deploy/gcloud_cors/`](/hunt/deploy/gcloud_cors/) to use your domains.
 1. Follow the instructions for [configuring CORS on a Google Cloud bucket](https://cloud.google.com/storage/docs/configuring-cors).
    ```
    gsutil cors get gs://CLOUD_BUCKET_NAME
    gsutil cors set hunt/deploy/gcloud_cors/prod-cors.json gs://CLOUD_BUCKET_NAME
    ```

### Follow-ups
 - You can run it on other web hosts or servers. You'll need a Python host that supports WebSockets. You may also need to build the puzzle assets before pushing. For our prod instance, we used Google App Engine's standard environment, and handled the WebSocket connections using a smaller number of Google App Engine's flexible environment and a VPC network.
 - You can set up CI/CD. We used Github Actions to automate pushing to both Heroku and Google App Engine, and you can [see our configs](/.github/workflows/).
 - You can set up your own domain instead of Heroku's. This requires modifying the DNS of your domain to verify you own it to Heroku, and so that Heroku can set up SSL automatically.
 - You can set up email receiving and parsing to support features like accepting email submissions for the scavenger hunt.
 - You can set up an email sending backend so that story and update emails are sent to solving teams.
 - You can [deploy static assets to a CDN](#appendix-exceeding-herokus-slug-size) and re-configure the app to use that instead.
 - You can scale to multiple instances. If you do this, you'll need to set up a [Django channels](https://channels.readthedocs.io/en/stable/) layer for inter-process communication as otherwise, interactive puzzles won't work correctly.

For most of the above, there are more details of how we did it in the [tech stack guide](tech-stack.md).
