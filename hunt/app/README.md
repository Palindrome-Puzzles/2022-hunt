# 2022 Hunt App
The Django app powering Palindrome's 2022 Mystery Hunt website. This contains hunt-specific logic and implementation details.

Business logic lives in [`hunt.app.core`](/hunt/app/core/). It uses [`spoilr`](/spoilr/core/) APIs to change the hunt state, listens for events like puzzles being solved, and has specific implementations of website pages like the overall template, FAQs, puzzle submission forms, and the hints UI.

It also contains common libraries for the [backends](special_puzzles/) and [frontends](scripts/) of special puzzles. A special puzzle is one that needs a custom server endpoint (for example, to hide information from solvers like a maze they're navigating), or teamwork to synchronize puzzle state across team members.

It also contains site-wide [styles](static/stylesheets/site.css) and [scripts](static/core/).

Views live in [`hunt.app.views`](views/), and are split into modules by their purpose.
 - They're guarded by common decorators from [`spoilr.core.decorators`](/spoilr/core/decorators/) or [`views.common`](views/common.py). For example, a decorator might verify that the team has access to a puzzle before they access the puzzle page, and automatically fill in the puzzle into the `request` object.
 - They should only basically query and collate information for the templates, with very little business logic.

The templates live in the [`hunt.app.templates`](templates/) folder. We use template inheritance to provide common page structure without duplication.

The [`top` templates](templates/top/) and [views](views/top_views.py) are bespoke pages within our hunt website such as the home page, updates/errata, FAQ, etc.
