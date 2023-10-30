import os

from pelican import signals

# TODO:: These should come from Pelican Config, OS, Default in that order.
STRAVA_ACTIVITIES_ENDPOINT = os.getenv(
    "STRAVA_ACTIVITIES_ENDPOINT", "https://www.strava.com/api/v3/activities"
)
# TODO:: When we pull this from pelican config, put a warning that we shouldn't keep
#  client secrets in the config
STRAVA_CLIENT_SECRET = ""


def add_article(articleGenerator):
    """Add strava article to pelican generator."""
    pass


def register():
    """Register article creation signals with pelican."""
    # TODO:: Add some form of "last generated" display
    signals.article_generator_pretaxonomy.connect(add_article())
