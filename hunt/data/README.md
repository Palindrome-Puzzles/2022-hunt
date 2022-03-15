# 2022 Hunt Data
This package contains all puzzle-related data for the hunt. This includes:
 - puzzles: the data needed to render puzzles and their solutions
 - rounds: the round-specific templates and meta-puzzles
 - hunt info: spreadsheets containing the list of puzzles, teams, rounds, interactions, etc with which to hydrate the database
 - special puzzle backends: the server endpoints for puzzles
 - puzzle view logic: [template tags](templatetags/) for manipulating [common page data](../app/views/common.py) into puzzle-specific data structures

## Puzzles
For each puzzle, the puzzles directory contains:
 - some metadata about the puzzle that is exported from puzzup
 - the assets required to display the puzzle

If a puzzle also requires a custom endpoint on the hunt server, there should additionally be a module within `hunt.data.special_puzzles` to implement the custom endpoint.

For the following, paths are given relative to this `hunt.data` package.

(You may also want to read the [forking guide](/docs/fork.md).)

### Directory structure
Each puzzle has a unique URL at which they will be accessible. This URL should be hyphen separated, such as `my-puzzle-url`.

The following files can be present:
 - `puzzle/<puzzle-url>/metadata.json` (required): a JSON file that is normally exported from puzzup. It has the following keys:
    - `puzzle_idea_id` (required): the puzzup ID of the puzzle
    - `puzzle_slug` (required): the same as `<puzzle-url>`
    - `puzzle_title` (required): the title to display for the puzzle
    - `answer` (required): the correct answer to the puzzle in canonical form
    - `credits` (required): the possibly-empty credits for the puzzle
    - (+ some additional credits-related fields)
 - `puzzle/<puzzle-url>/config.json`: a JSON file with config that is not exported from puzzup, and is instead manually managed. It has the following keys:
    - `pseudo`: a object with pseudo-answers (in canonical form) as keys and the corresponding responses as values
 - `puzzle/<puzzle-url>/hints.json`: a JSON file that is normally exported from puzzup. It is an array of hints, where each hint is an array with these three entries:
    - index `0`: the order of the hint
    - index `1`: a possibly empty array of keywords for the hint
    - index `2`: the text of the hint
 - `puzzle/<puzzle-url>/index.html` (required): a partial HTML file with the puzzle content
 - `puzzle/<puzzle-url>/style.css`: a CSS file with styles that are specific to this puzzle's content only
 - `puzzle/<puzzle-url>/solution/index.html` (required): a partial HTML file with the solution content
 - `puzzle/<puzzle-url>/solution/style.css`: a CSS file with styles that are specific to this puzzle's solution only

There is also an optional `posthunt/` folder with a similar specification to the `solution` folder.

You can also build puzzle assets. For more details, please see the [fork documentation](/docs/fork.md#postproduction-bundle).

### File content
The `index.html` files are _partial HTML files_. This means there's no need for `doctype`, `html`, `head`, `body`, tags, etc. Just write the HTML tags you need to describe your puzzle. Then this gets read by Django and inserted into the round template for the puzzle's round.

Your `index.html` and `style.css` can import other files. (For CSS, see [`@import`](https://developer.mozilla.org/en-US/docs/Web/CSS/@import)). When doing so, you can just use ordinary relative URLs and the server automatically rewrites them to find the static file properly.
 - If the file is in your puzzle directory: `<img src="images/0.png">`.
 - If the file is a shared library or javascript file (such as those in [`hunt.app.static`](/hunt/app/static/)), then use the `static` tag to load it. For example, `<script src="{% static lib/jquery.min.js %}"` or `@import 'stylesheets/map.css';`
 - If the file needs to be cache-busted, then add a dummy query string to the asset, such as `images/0.png?v=1`. This can be useful if an image is updated mid-hunt, so that teams immediately see the new version when they refresh the page.

For solutions, the `index.html` and `style.css` now have access to both files in their `solution/` directory, or in the parent puzzle directory. For example, they might re-include all the images from the puzzle and caption them with the letter extracted from it. Or they might need a new image showing a filled-in version of the puzzle image.
 - To access files from the puzzle directory, use `../images/0.png` as before.
 - To access files from the solution directory, use `images/0.png`.

Likewise, the `posthunt/` directory can access solution or puzzle content using relative paths.

### View logic
Some puzzles (especially metapuzzles) collate information when rendering. You can handle this with [template tags](templatetags). See existing puzzles for some examples.

### Postproduction
Please see the [postproduction guide](/docs/postproduction.md).

## Rounds
For each round, the rounds directory contains:
 - some templates for how to render puzzles and solutions within the round
 - templates for how to render the round page and round solution
 - the round solution

For the following, paths are given relative to this `hunt.data` package.

### Directory structure
Please see the [forking guide](/docs/fork.md#round-bundles).

### File content
To access static files, you can use the following tags:
 - `{% rd '0.png' %}` to access files within the round directory
 - `{% rd '0.png' solution=True %}` to access files within the round solution directory
 - `{% static 'lib/jquery.min.js' %}` to access shared static files

### Hunt info
A bunch of TSV files describing how the hunt is configured.

Please see the [forking guide](/docs/fork.md#puzzle-and-round-configuration).
