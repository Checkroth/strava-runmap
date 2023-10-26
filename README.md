strava_runmap: A Plugin for Pelican
===================================

[![Build Status](https://img.shields.io/github/actions/workflow/status/pelican-plugins/strava_runmap/main.yml?branch=main)](https://github.com/pelican-plugins/strava_runmap/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-strava_runmap)](https://pypi.org/project/pelican-strava_runmap/)
[![Downloads](https://img.shields.io/pypi/dm/pelican-strava_runmap)](https://pypi.org/project/pelican-strava_runmap/)
![License](https://img.shields.io/pypi/l/pelican-strava_runmap?color=blue)

Hooks in to Strava API to create a page of all of your historical runs in strava.

## Requirements

This plugin requires the pacakges in `requiremnets.txt` to be installed in the pelican implementation that is using this plugin.

Installation
------------

This plugin can (not yet) be installed via:

python -m pip install pelican-strava_runmap
As long as you have not explicitly added a `PLUGINS` setting to your Pelican settings file, then the newly-installed plugin should be automatically detected and enabled. Otherwise, you must add `strava_runmap` to your existing `PLUGINS` list. For more information, please see the [How to Use Plugins](https://docs.getpelican.com/en/latest/plugins.html#how-to-use-plugins) documentation.

Usage
-----

### Configuration

Environment variables / pelican configs: The following are environment variables names. They have the _same key as the environment variable name_ in `STRAVA_RUNMAP_CONFIG` in the pelican config (e.g. `STRAVA_RUNMAP_CONFIG = { "STRAVA_API_TOKEN": "abcd1234" }`
- `STRAVA_API_TOKEN`: a valid token is required to get activitiesto generate the runmap page.
- `STRAVA_ENDPOINT`: Defaults to `https://www.strava.com`, but is configurable. If you configure it, it must be:
  - A valid url scheme (start with http(s)://)
  - Not end in a slash (the plugin adds the trailing `/`)
- `STRAVA_DRY_RUN`: Evaluates to bool. Omit if it's not a dry run, fill it with anything if it is a dry run. Dry run fills with a few test images, but does not actually hit the strava API (use this if you haven't got a token yet or are repeatedly re-generating and want to speed things up and avoid getting rate-limited.)

### Setting up strava

Requires `STRAVA_API_TOKEN` environment variable when building your site. You can get this token by following the [Strava Guide].

Because this plugin does not keep track of your actual strava details (including access and refresh tokens), once the token you generate with Strava expires you will have to generate a new one via their web interface (or whatever method you prefer). If you know if a better way to do this, please feel free to submit a pull request :)

Some tips:

- You can get your key from the [strava application page] once you have set it up.
- The token is rate limited. Unless you have a HUGE amount of activities or are constantly rebuilding, you shouldn't hit it.
  - If you are doing a trial/error and want to avoid using your quota, set your config or environment variable `STRAVA_DRY_RUN=1` . This will generate a few dummy maps for layout testing and preview, without using up your quota.

Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues].

To start contributing to this plugin, review the [Contributing to Pelican] documentation, beginning with the **Contributing Code** section.

License
-------

This project is licensed under the AGPL-3.0 license.

[existing issues]: https://github.com/pelican-plugins/strava_runmap/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html
[Strava Guide]: https://developers.strava.com/docs/getting-started/#account
[strava application page]: https://www.strava.com/settings/api
