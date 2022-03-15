# Github Actions configuration
This directory defines our automatic deployments to each environment. It has some optimizations like avoiding concurrent builds, minimising the Python requirements installed for each push, and using cached pip installations. This helped reduce one of our major expenses - Github Actions minutes.

The workflows are for:
 - Deploying the nuke cache cloud function automatically when the source is edited.
 - Deploying static assets to Google Cloud Storage.
 - Importing the latest puzzles and teams to Google App Engine.
 - Importing the latest puzzles and teams to Heroku.
 - Releasing to Google App Engine. This handles both the frontend and backend services.
 - Releasing to Heroku.

Many of these workflows have prod and staging variants.

For Google Cloud, each composite action has its own way of authenticating, so there's a bunch of boilerplate passing authentication tokens around. However, they're deprecated now, for presumably the future's [one true way](https://xkcd.com/927/).
