# 2022 MIT Mystery Hunt

## About
This repository contains the Django project, website, CI/CD configuration, build scripts, and management commands for Palindrome's 2022 MIT Mystery Hunt.

You can learn more about the [MIT Mystery Hunt](https://puzzles.mit.edu/), or view the [2022 Hunt website and puzzles](https://www.starrats.org/).

You may be interested if this repository if you're:
 - [re-running the hunt for your team](docs/deploy.md) with hunt-style unlocking and [managing the hunt as it runs](docs/manage.md),
 - [creating your own hunt](docs/fork.md) and want to fork this codebase,
 - [merging some of our features into your own hunt](docs/features.md), or
 - [reading about the tech stack and infrastructure](docs/tech-stack.md) as a guide for running your own MITMH-scale event.

This repository is not formally maintained and responding to emails or PRs is best-effort. (But we'll especially do our best to merge in fixes for the recently-broken [copy-to-clipboard feature](docs/features.md#copy-to-clipboard)!)


## Getting started
**Note**: When running the server or managing it, you need to provide a `DJANGO_ENV` environment variable. The commands below will show how to do this in bash. If you're using a different platform, make sure to change how you pass the environment variable as follows:
 - In bash, run `DJANGO_ENV=dev python manage.py runserver`
 - In PowerShell, run `$env:DJANGO_ENV='dev'; python manage.py runserver`
 - In Window's `cmd.exe`, run `set DJANGO_ENV=dev` first, and then run the commands below without any prefix. However, bash commands like `mkdir` won't work, so really just use PowerShell instead.

**Note**: You may need to use `python3` instead of `python` in the commands below, depending on how Python is installed in your environment.

### Initial setup
> **Note**: The public version of this repository does not enable [Git Large File Storage (LFS)](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage), so it can be cloned without counting against Palindrome's LFS bandwidth. If [forking](docs/fork.md) to make changes, we recommend enabling LFS by [following these instructions](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) and if necessary, [migrate files](https://github.com/git-lfs/git-lfs/wiki/Tutorial#migrating-existing-repository-data-to-lfs).
>
> Our `.gitattributes` config was:
> ```
> *.wav filter=lfs diff=lfs merge=lfs -text
> *.mp3 filter=lfs diff=lfs merge=lfs -text
> *.mp4 filter=lfs diff=lfs merge=lfs -text
> *.pdf filter=lfs diff=lfs merge=lfs -text
> ```

The first-time you want to develop or run the server, do the following.
 1. Install [`Python 3.9+`](https://www.python.org/downloads/) and if needed, [`pip`](https://pypi.org/project/pip/) (which should be part of your Python install already).
     - On Windows, make sure you [add the Python install location to the `PATH`](https://docs.python.org/3/using/windows.html#finding-the-python-executable). You can tell if it worked by typing `python` into a command prompt.
 1. Make a directory to store hunt code.
    ```
    mkdir -p path/to/hunt
    cd path/to/hunt
    ```
 1. Clone the `2022-hunt` repository.
    ```
    git clone https://github.com/Palindrome-Puzzles/2022-hunt.git
    ```
 1. Move into the `2022-hunt` repo. All following commands will be run from this directory.
    ```
    cd 2022-hunt
    ```
 1. (Windows only) Fix symlinks if necessary. In an **admin PowerShell**, run the following script.
    ```
    bin\fix-symlink-windows.ps1
    ```
     - **Why**: This repository uses symlinks so that [puzzles](hunt/data/puzzle) and [rounds](hunt/data/round) can be postprodded ergonomically while also making the files available where Django expects them to be.
     - In Windows, symlinks require admin rights to create, so Git doesn't create them unless you were already an admin when you cloned/pulled the repo. This script repairs the symlinks.
 1. Set up a [virtual environment](https://docs.python.org/3/library/venv.html).
    ```
    python -m venv env
    ```
     - **Why**: This lets Python dependencies can be installed and isolated from the system Python installation.
 1. Activate the virtual environment.
     - In PowerShell and `cmd.exe`, run `env\Scripts\activate`.
     - In bash, run `source env/bin/activate`.
     - (To deactivate, run `env\Scripts\deactivate\` or `source env/bin/deactivate`.)
 1. Install Python dependencies.
    ```
    pip install -r requirements/dev.txt
    ```
     - **Why**: This repository supports multiple environments, and uses a minimal set of dependencies in the dev environment. For example, we use [SQLite](https://www.sqlite.org/index.html) instead of Postgres for portability and ease-of-setup.
 1. Setup your new database. This will create and use an [SQLite](https://www.sqlite.org/index.html) `db.sqlite3` file in the `path/to/hunt/2022-hunt` directory.
    ```
    DJANGO_ENV=dev python manage.py migrate
    ```
 1. "Launch" the hunt locally. This imports some admin teams, the 2022 puzzles, and configures the website state so that teams can register and solve puzzles.
    ```
    DJANGO_ENV=dev python manage.py importteams
    DJANGO_ENV=dev python manage.py importpuzzles

    DJANGO_ENV=dev python manage.py launch registration
    DJANGO_ENV=dev python manage.py launch rd0
    DJANGO_ENV=dev python manage.py launch rd0-released
    DJANGO_ENV=dev python manage.py launch hunt
    ```

### Building puzzles
Some puzzles in the hunt have a separate build process that compiles [Typescript](https://www.typescriptlang.org/) and [SCSS](https://sass-lang.com/) code to raw Javascript and CSS. If you'd like to view and solve these puzzles, then perform the following steps.
 1. Install [Node](https://nodejs.org/en/download/). This was developed using [Node 14](https://nodejs.org/en/blog/release/v14.19.0/), but newer versions should be fine too.
 1. Install dependencies for this repository.
    ```
    cd path/to/hunt/2022-hunt
    npm install
    ```
 1. Then either:
     - Run `npm run build` to build puzzle files.
     - Run `npm run watch` to continuously build puzzle files, and re-build them whenever they are changed. (This is useful when actively developing!)

> Note: The script will automatically minify bundles and include sourcemaps if your `DJANGO_ENV` starts with `prod_`.

> **Warning**: Running the build process on Windows can give a different output compared to non-Windows machines (say Github Actions or Heroku). This is because `esbuild` uses `\n` or `\r\n` depending on the environment, which changes content hashes and so filenames. This can be avoided if you minify bundles and skip sourcemaps.

### Running the server
To run the server, use the following command.
```
DJANGO_ENV=dev python manage.py runserver
```

The following URLs will be available.
 - <http://localhost:8000> to access the solver-facing hunt website.
 - <http://registration.localhost:8000> to access the hunt registration website.
 - <http://localhost:8000/hq/> to access the hunt management interface (HQ). This is for the hunt team during the hunt to see how solvers are progressing, mark off interactions as complete, process hints, respond to incoming emails or help requests, and more.
 - <http://localhost:8000/hq/admin/> to access the Django admin panel. This is for viewing and editing database models directly. Please be very careful in here, as it has the potential to break the hunt.
 - <http://localhost:8000/puzzlelzzup/> to see [Puzzleviewer](hunt/puzzleviewer). This lets you browse postprodded puzzles regardless of the hunt state. This is great for postprodders or factcheckers who don't need the whole hunt website running.

For the solver-facing hunt website, you can either use a team defined in [teams.tsv](hunt/data/hunt_info/teams.tsv), or register a new team. The admin teams in [teams.tsv](hunt/data/hunt_info/teams.tsv) have special privileges like accessing puzzles that are still locked, or shortcuts to auto-solve puzzles.

For the admin panels, you will need to log in as a team with admin rights from [teams.tsv](hunt/data/hunt_info/teams.tsv). For Puzzleviewer, you will need to log in as any non-public team from [teams.tsv](hunt/data/hunt_info/teams.tsv).

**Note**: On Macs using browsers other than Chrome, you probably need to [edit `/etc/hosts`](https://stackoverflow.com/questions/38905207/how-to-test-sub-domains-on-my-localhost-on-a-mac) to allow sub-domains of `.localhost` to be resolved.


## Further documentation
Some modules have further documentation:
 - [`.github/workflows`](.github/workflows) for our CI/CD setup using Github Actions
 - [`hunt/app`](hunt/app) for the code and infrastructure for the 2022 hunt website
 - [`hunt/app/special_puzzles`](hunt/app/special_puzzles) for a framework for writing interactive puzzles
 - [`hunt/data`](hunt/data) for all 2022 hunt puzzle and round related data including postprodded puzzle bundles. Some of the data is automatically pushed to this repo. For example, [PuzzUp](https://lol.puzzup.lol/) will push puzzle content when a postprodded bundle is uploaded, and generate `metadata.json` and `hints.json` files automatically
 - [`hunt/data_loader`](hunt/data_loader) contains utilities to load hunt data in a packaging-agnostic way
 - [`hunt/deploy`](hunt/deploy) is a thin wrapper Django project. It contains scripts and configs to start the hunt server locally, or to deploy to staging/production environments
 - [`hunt/puzzleviewer`](hunt/puzzleviewer) is a tool to postprod and factcheck puzzles without going through the full hunt website
 - [`hunt/registration`](hunt/registration) is the 2022 registration website

The [`spoilr`](spoilr/) package is a hunt-agnostic Django project to manage hunt state, and provide an admin panel for managing a live hunt.

There is also project-level documentation:
 - [archiving](docs/archive.md) the hunt website
 - [deployment guide](docs/deploy.md) for how to run your own version of the 2022 hunt
 - [editor setup](docs/editor.md) for tips on setting up your editor
 - [features](docs/features.md) for a summary of new and enhanced features in the 2022 hunt. You may be interested if running your own hunt, as it provides ideas and code links
 - [forking guide](docs/fork.md) for some tips on forking this codebase to run your own hunt
 - [future work](docs/future.md) for future work and TODO tasks
 - [management guide](docs/manage.md) for how to manage a live hunt
 - [postproduction guide](docs/postproduction.md) for an export of the internal postproduction guide we developed for our postprodding team
 - [tech stack overview](docs/tech-stack.md) for an overview of our tech stack, as a starting point if you're running an MITMH-scale event


## Acknowledgements
This project draws from and is inspired by earlier Hunt websites. Much of the direction was influenced in particular by [Galactic's 2021 MIT Mystery Hunt](https://github.com/YewLabs/silenda) (and their [secondary repo](https://github.com/YewLabs/2021-hunt/)).

## Similar projects
An incomplete list of other hunt websites:
 - Galactic: https://github.com/galacticpuzzlehunt/gph-site
 - Teammate: https://gitlab.com/teammate/tph-site

## Contributors
### Tech lead
 - [Sahil Bhasin](https://github.com/sb3700)

### Tech team
 - [Dan Lepage](https://github.com/dplepage)
 - [Jacob Ford](https://github.com/unitof)
 - [James Sugrono](https://github.com/jimsug)
 - [Isaac Garfinkle](https://github.com/Igarfinkle)
 - [Matt Cleinman](https://github.com/mcleinman)
 - [Sandy Weisz](https://github.com/santheo)
 - [Shai Nir Hana](https://github.com/ShaiNir)
 - [Shawn Ligocki](https://github.com/sligocki)

### Postproduction team
 - [Aaron Fuegi](https://github.com/aarondf1)
 - [Ashley Davis](https://github.com/andmade)
 - [Ben Smith](https://github.com/BenMSmith)
 - [Daniel Hunt](https://github.com/Carostark)
 - [Deborah Levinson](https://github.com/debbylevinson)
 - [Foggy Brume](https://github.com/foggybrume)
 - [Isaac Garfinkle](https://github.com/Igarfinkle)
 - [Jacob Ford](https://github.com/unitof)
 - [James Sugrono](https://github.com/jimsug)
 - [Jen McTeague](https://github.com/imperiosaur)
 - Joe Cabrera
 - Kieran Boyd
 - [Mike Seplowitz](https://github.com/mikesep)
 - [Phil Steindel](https://github.com/remotelytrue)
 - [Sahil Bhasin](https://github.com/sb3700)
 - [Sandy Weisz](https://github.com/santheo)
 - [Shai Nir Hana](https://github.com/ShaiNir)
 - [Shawn Ligocki](https://github.com/sligocki)

## License
This project has different licenses for different sections of the codebase.
 1. The following puzzles are licensed under the [Creative Commons Attribution Non-Commercial No-Derviatives license](LICENSE.cc-by-nc-nd.txt).
     - [Curious and Determined](/hunt/data/puzzle/curious-and-determined)
     - [Sorcery for Dummies](/hunt/data/puzzle/sorcery-for-dummies)
     - [The Times They Had](/hunt/data/puzzle/the-times-they-had)

 1. All images, sounds, and videos are licensed under the [Creative Commons Attribution Non-Commercial No-Derviatives license](LICENSE.cc-by-nc-nd.txt).

 1. All fonts are co-located with their own license.

 1. Anything else within the [`hunt/data`](hunt/data) folder is licensed under [Creative Commons Attribution Non-Commercial license](LICENSE.cc-by-nc.txt).

 1. Everything else in the repository is licensed under the [MIT license](LICENSE.mit.txt).

If there are questions about the licensing, please contact Palindrome.
