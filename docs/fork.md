# Making your own hunt
If you're forking this repository with the intent to create your own hunt, this page highlights places to modify code.

As a pre-requisite, please follow the [getting started instructions](../#getting-started) on the repository home page. I recommend the optional step of setting up LFS if you're actively working on this repository.

You can also read our [deployment quickstart guide](deploy.md), how to [manage the hunt](manage.md), and our [tech stack](tech-stack.md) as inspiration.

**Note**: At serve-time, we access files from within [`/hunt/data/`](/hunt/data/) using a "data loader" abstraction in [`/hunt/data_loader/`](/hunt/data_loader/). This isn't strictly necessary any more, but was needed when we at an earlier point, had our repo split across multiple PIP packages. However, we've kept it as it provides a good abstraction layer over accessing files compared to working with raw file paths.


## Puzzles and rounds
### Metadata
We used [puzzup](https://github.com/Palindrome-Puzzles/puzzup) (our fork of [puzzlord](https://github.com/galacticpuzzlehunt/puzzlord)) to edit, manage and testsolve puzzles. This was the source of truth for most puzzle metadata such as names, answers, URLs, credits, canned hints, etc. It also defined a stable "puzzle external ID" that we used to refer to the puzzle in both code and in Palindrome internal communication.

We set up set up some ways to export this metadata from Puzzup including a way for the postproduction team to get the metadata for a specific puzzle, and a one-way synchronisation process to update the metadata for all puzzles. These processes are out-of-scope for this documentation.

### Postproduction bundle
Each puzzle has a "postproduction bundle" at the following codepath: `/hunt/data/puzzle/<URL for puzzle>/`. (The URL was chosen to avoid containing slashes, having trailing dots, and other things that broke some OS/Git/browser.)

Each postproduction bundle can contain the following files:
 - [required] `index.html` (or `index.template.html` if it uses Typescript) - the (partial) HTML for the puzzle content (excluding tags like `html`, `body`, etc).
 - [required] `metadata.json` with puzzle metadata
 - `style.css` (or `style.scss` if it uses SASS) - the puzzle-specific styles, so they can be placed in he document `head` appropriately.
 - `solution` folder containing `index.html` for the puzzle's solution, and an optional `style.css`
 - `posthunt` folder containing `index.html` for the posthunt version of the puzzle, and an optional `style.css`
 - `hints.json` containing canonical hints. This is an array of arrays, and each child array has 3 elements: a number used to order the hints, an array of hint keywords, and the hint text itself. (This was the data structure exported from puzzup.)
 - `config.json` containing extra puzzle-specific behavior. We only used this for puzzle "pseudoanswers", where we gave a confirmation or nudge in response to certain phrases.
 - `__build` folder containing Typescript files, and where the output can be embedded into a puzzle file using special tags. Take a look at [The Messy Room](/hunt/data/puzzle/the-messy-room/) to see how to use the feature. If present, the puzzle should use `index.template.html`, so the special tags can be expanded.
 - `main.ts` for a Typescript bundle to use in the puzzle. If present, the puzzle should use `index.template.html`, so the reference to `main.ts` can be rewritten.
 - any other images/scripts/assets that can be referred to using the relative path in CSS or HTML files. These references are automatically rewritten at serve time, including verifying permissions like "the puzzle can't use assets in the `solution` directory".

Once the postproduction bundle exists, it can be viewed and tested in [Puzzleviewer](features.md#puzzleviewer). This is how we tested puzzles during development, and how we testsolved puzzles. Puzzleviewer takes care of things like injecting the site-wide stylesheet so our common postproduction styles are available.

There are some more docs available in the [`hunt.data` package](/hunt/data/#puzzles).

### Round bundles
Rounds have a more involved process, as they're often more complex. Each round has a bundle at `/hunt/data/round/<URL for round>/`. There were also some pseudo-rounds such as the prologue, endgame and events rounds that had special serving rules.

Each contains several Django templates that are responsible for the whole page. As a result, they used Django template inheritance to share code. The files that can be present are:
 - `puzzle.tmpl` - a wrapper for puzzle pages
 - `puzzle_solution.tmpl` - a wrapper for puzzle solution pages
 - `round.tmpl` - the round map page
 - `round_common.css` - a common stylesheet injected into every page on the round
 - `style.css` - a stylesheet injected into the round map page only
 - `subview.tmpl` - a wrapper for "extra content" within the round, such as the book reports page in The Ministry
 - `answer.mp3` - the sound to play when a puzzle is solved within the round
 - `manifest.py` - the config for [stickering the round map](features.md#round-maps)

These build upon the generic templates in [`/hunt/data/round/`](/hunt/data/round/).

The round map stickering logic is largely in [`/hunt/app/views/round_views.py`](/hunt/app/views/round_views.py).

> **Note**: We removed all solve sounds from this repository before sharing it publicly.

### Puzzle and round configuration
The association of puzzles to rounds, and the configuration for puzzle unlock order is in [`/hunt/data/hunt_info/`](/hunt/data/hunt_info/).

[`rounds.tsv`](/hunt/data/hunt_info/rounds.tsv) defines the list of rounds and some basic parameters like their display name and ordering.

[`puzzles.tsv`](/hunt/data/hunt_info/puzzles.tsv) defines the list of puzzles, the associated round and "puzzle external ID", and the ordering within each round. It then contains some parameters specific to our [unlocking rules in 2022](#unlocking-puzzles), and that may need to be changed for your hunt.

**Note**: The Django models reflect the division between common puzzle logic, and hunt-specific hunt logic. For example, [`/spoilr/core/models.py`](/spoilr/core/models.py) contains the common `Puzzle` model with fields we think are common to all hunts, and [`/hunt/app/models.py`](/hunt/app/models.py) contains 2022-specific puzzle fields in `PuzzleData`. (These models are related using a 1-to-1 relation and the queries mostly prefetch data from both models at once, so this division doesn't cause any discernible performance issues.)

If you've changed the puzzles, round, or teams CSVs, you will need to re-run `importteams` or `importpuzzles` as described on the [home page](../). If puzzle data or the TSVs are configured incorrectly, the import script may silently fail and print an error so do read the logs if stuff is misbehaving.


### Auxiliary assets
We had a concept of auxiliary assets for pseudorounds. These could be accessed using the `{% aux .. %}` template tag, and were scoped by the pseudoround they belonged to.

This was useful for code organization, but otherwise, these could have just been part of the `static` directory. The one exception is that we programatically accessed the Pen Station `manifest.py` to render the round map for Pen Station, and so only having a static URL would not work well.

### Interactive puzzles
There's a common framework for writing the frontend and backend of interactive puzzles. You can see [`/hunt/app/special_puzzles/`](/hunt/app/special_puzzles/) or [the feature summary](features.md#framework-for-writing-interactive-puzzles) for more information.

### Complex puzzle rendering
Some puzzles require more information manipulation, such as our meta puzzles needing to know what puzzles are unlocked. We solved this using [template tags](/hunt/app/templatetags/) for round-specific view logic. This manipulated information available in the context for all pages as defined in [`/hunt/app/views/common.py`](/hunt/app/views/common.py).


## Teams
In 2022, teams were modelled as:
 - a `Team` entity (plus some associated 2022-specific `TeamData`)
 - a shared `User` entity that integrated with the Django authentication system

The shared `User` was given the role `SHARED` to reflect that it was a common account, and so this system can be extended to allow multiple users within a team.

[`teams.tsv`](/hunt/data/hunt_info/teams.tsv) defines some built-in teams.
 - `admin` is set up as a superuser with full access to the Django admin panel and our `spoilr` HQ. It also has special powers on the website like accessing locked puzzles, or using shortcuts to solve/unsolve puzzles
 - `internal` is an ordinary user except:
    - it can access Puzzleviewer for internal testing
    - it won't show up in the teams list in the registration website
 - `public` is a special user that can be used when the hunt is complete to access all puzzles

In the future, we recommend adding another type of user that has readonly access to HQ. This lets all members of the team see team progress, without necessarily having the powert to answer emails, respond to hints, etc if they haven't been trained.


## Hunt logic
Most 2022-specific hunt logic lives in [`/hunt/app/core/`](/hunt/app/core/) by design. We make heavy use of an event dispatcher in [`/spoilr/core/api/events.py`](/spoilr/core/api/events.py) to separate core behaviour feom 2022-specific behaviour, and the callbacks are largely defined in [`/hunt/app/core/callbacks.py`](/hunt/app/core/callbacks.py).

### Middleware
A bunch of common middleware is defined in [`/hunt/app/views/common.py`](/hunt/app/views/common.py) and [`/hunt/app/core/hosts.py`](/hunt/app/core/hosts.py). In some combination, this affects most pages in the site and so it's a good place to inspect and tweak default behavior.

### Unlocking puzzles
Puzzle unlocking is controlled by [`/hunt/app/core/puzzles.py`](/hunt/app/core/puzzles.py) and configured in [`/hunt/data/hunt_info/puzzles.tsv`](/hunt/data/hunt_info/puzzles.tsv).

If you're adapting our puzzle unlock logic, a downside to consider is that in each Act 3 round, there are normally 2 unlocked puzzles. However, if you solve a puzzle and unlock a new round, it reduces to 1 unlocked puzzle (and then 0 if you do it again). That can make choke points in certain rounds and be frustrating. We made a deliberate decision to proceed with this tradeoff and it was mostly fine.

### Team notifications
Team notifications are defined in [`/hunt/app/core/callbacks.py`](/hunt/app/core/callbacks.py) and [`/hunt/app/core/story_callbacks.py`](/hunt/app/core/story_callbacks.py). They're implementd in [`/hunt/app/static/core/site.js`](/hunt/app/static/core/site.js).

### Hints
Hints are released when a certain number of teams have solved a puzzle, with some extra override flags for puzzles that are especially hard. The hint release time is set up in `update_hints_release_delay` in [`/hunt/app/core/callbacks.py`](/hunt/app/core/callbacks.py), and the rest of the logic is part of [`/hunt/app/views/puzzle_hint_views.py`](/hunt/app/views/puzzle_hint_views.py).

### Email handling
2022-specific email handlers are set up in `unlock_email_interactions` in [`/hunt/app/core/interactions.py`](/hunt/app/core/interactions.py). There's also some relaying behaviour defined in [`/spoilr/core/email/views/incoming_views.py`](/spoilr/core/email/views/incoming_views.py) that is controlled by some Django settings.

### Rewards and free answer tokens
Reward and free answer logic is defined in [`/hunt/app/core/rewards.py`](/hunt/app/core/rewards.py).

### Story
Story beats data is stored in [`/hunt/data/hunt_info/story.tsv`](/hunt/data/hunt_info/story.tsv), and the behavior is configured in [`/hunt/app/core/story.py`](/hunt/app/core/story.py).

### URL structure
Pages for the site are set up in [`/hunt/app/core/views/`](/hunt/app/core/views/) and configured in [`/hunt/app/core/urls.py`](/hunt/app/core/urls.py). Most of them are general pages that can be tweaked for your hunt. Stuff in `magic_views.py`, `top_views.py` and `manuscrip_views.py` will probably need to be updated though.


## Interactions
Interactions are when HQ needs to perform some action such as grading a submission or performing a check-in before a team can proceed. Interactions are a very generic (and confusing) concept - for example, an interaction is created when we receive an email submission for New You City, because that's the point at which HQ needs to act.

Interactions are set up in [`/hunt/data/hunt_info/interactions.tsv`](/hunt/data/hunt_info/interactions.tsv), 2022-specific behavior is largely in [`/hunt/app/core/interactions.py`](/hunt/app/core/interactions.py) although it's also elsewhere like in [`/hunt/app/views/manuscrip_views.py`](/hunt/app/views/manuscrip_views.py), and the HQ integration is implemented as plugins in [`/spoilr/interaction/`](/spoilr/interaction/). The UI and workflows for this could definitely be improved if your team has bandwidth.


## Deployment configuration
Please see [deploy.md](deploy.md) for a case-study deployment and a guide in where configuration lives. You can see [tech-stack.md](tech-stack.md) for our actual tech stack. And [`/.github/workflows/`](/.github/workflows/) contains our CI/CD configuration.


## Postproduction lessons
After postproducing many puzzles, here are some tips:
 - Avoid flexbox for layout if you can instead use the standard CSS box model. Flexbox breaks the styles for controlling page breaks in print such as `break-inside: avoid-page;` in some browsers. For example, if you're trying to make a 2-column responsive layout, use `display: inline-block; width: 49%;` instead.
 - Test in print early, as often issues crop up that are otherwise hard to predict. Use a helper class like `.keep-colors-in-print` for informational background colors.
 - If styles are common to multiple puzzles, consider extracting them to a shared class. This helps keep puzzles visually cohesive, and makes overall maintenance easier. For example, we standardised all grid and crossword styles early, and invested effort in making them modular enough to work for as many puzzles as possible.
 - Screenshots in our [postproduction guide](postproduction.md) were very valuable.


## Staging/production checklist
If deploying to a shared environment such as staging or production, there are a few extra things you MUST do.

### Production-ready settings
See [settings](/hunt/deploy/#production-ready-settings) for how to ensure the server will be secure.

### Authentication
Use a secure password for any Django superusers or staff users. These have full access to the server's database, and to HQ, so very few people should know it.

When running in staging, you MUST use a secure password for any test teams. The staging environment will be open to the public, and give access to all puzzles in development. To ensure only our team has access, the passwords should be secure and unguessable.

### Channel layer
When deploying across multiple servers/processes, we need a channel layer to allow those servers/processes to communicate. This communication is needed for features like broadcasting to team members, or enabling teamwork puzzles. We use [Django channels](https://channels.readthedocs.io/en/stable/) to support this, and it needs a "channel layer" backend to relay messages.

In production, a channel layer needs to be deployed such as [channels_redis](https://github.com/django/channels_redis/).

### Caching
Some Django views are commonly used (such as a team's puzzle page), or expensive to compute (such as HQ dashboards). A cache that is shared across multiple servers/processed can reduce server load and make the hunt website faster.

In production, a [cache server](https://docs.djangoproject.com/en/3.2/topics/cache/) such as [memcached](https://docs.djangoproject.com/en/3.2/topics/cache/#memcached) or [redis](https://github.com/jazzband/django-redis) needs to be configured.

### Deploy static assets
Django can automatically serve static assets. However, this is grossly inefficient and probably insecure (as per the Django docs) so cannot be used outside local development.

Another issue that might occur is that Django has an [issue where serving static files fails](https://github.com/django/channels/issues/1722). This is a guard to avoid deadlocks due to thread exhaustion, and can occur if you fetch lots of files rapidly when developing. Serving static files properly can avoid this issue.

Take a look at the [deployment guide](deploy.md#appendix-exceeding-herokus-slug-size) for how we did it.

### Continuous deployment
You may want to set up continuous deployment so that changes to the repo are automatically pushed to our shared environments. This helps split release duties and reduces the amount of training needed.
