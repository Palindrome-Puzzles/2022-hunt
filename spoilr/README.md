# Spoilr (HQ)
A Django project to handle hunt-agnostic puzzle management for puzzle hunts such as the MIT Mystery Hunt.

## Features
 - Models, API and events system for common hunt behaviour.
 - Managing incoming interactions, hint requests, contact requests, and emails.
 - General [task management](#tasks) framework for incoming items.
 - Progress dashboards.
 - Logging system.
 - Settings system.
 - Lifecycle management.
 - Common view decorators.
 - User/team authentication and impersonation.

See [our features guide](/docs/features.md#hq) for more about spoilr/HQ.

## Design philosophy
It provides a [`core`](core/) package with models and APIs common to most hunts.  The [`core`](core/) package aims to have no dependencies on other spoilr packages, or on code specific to the 2022 hunt.

It also provides a series of plugin apps for features such as email management or progress dashboards. This encapsulation of features into their own Django app is to better organize code, and to make selecting individual features for reuse simpler. Each plugin app is responsible for one feature, and should mostly depend on only `spoilr.core`. However, it may depend on other apps or on 2022-hunt specific code where appropriate, such as a dashboard showing 2022-specific features.

There's also the [`hq`](hq/) package. It contains the HQ home page dashboard, some common stylesheets, and some utility views and behaviours such as [task management](#tasks). It also contains some "legacy URLs" that haven't been migrated to the plugin-style architecture yet.

## Tasks
Spoilr surfaces tasks for HQ to act upon so the hunt can proceed. We've defined common models and actions for tasks such as claiming them, snoozing them, and resolving them. These are used throughout other spoilr plugins as appropriate.

## Tick
See the [management docs](/docs/manage.md#ticking-the-hunt).

## Future work
This refresh of spoilr is very much a work-in-progress, as our tech team had to focus on the hunt website & puzzle postproduction first. There are many usability issues and features we'd love to fix/add, and many of these are captured in our [future work guide](/docs/future.md).

I'd like to highlight the following features we dropped from the 2021 hunt repo:
 - [Discord logging](https://github.com/YewLabs/silenda/blob/master/spoilr/log.py#L42) - Could be implemented by calling webhooks in [`send_to_discord` in the 2022 callbacks config](/hunt/app/core/callbacks.py).
 - [Discord queue bot](https://github.com/YewLabs/silenda/blob/master/spoilr/log.py#L61) ([bot](https://github.com/YewLabs/silenda/tree/master/queuebot)) - This created/deleted messages in a Discord channel when tasks (like a hint request) were created/unsnoozed or resolved/snoozed. This could be integrated with our general [task framework](#tasks).
 - [Post-puzzle surveys](https://github.com/YewLabs/silenda/blob/master/spoilr/submit.py#L200)

## Acknowledgements
This is heavily influenced by the [2021 hunt's version of spoilr](https://github.com/YewLabs/silenda/tree/master/spoilr).
