from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime

from pelican import contents, generators, signals, settings

from . import _strava_interface, _svg_interface


STRAVA_RUNMAP_KEY = 'STRAVA_RUNMAP'
STRAVA_RUNMAP_SETTINGS = {
    "CLIENT_ID": "",
    "CLIENT_SECRET": "",
    "AUTH_CODE": "",
}

@dataclass
class SvgPageContext:
    display_name: str
    display_date: date
    svg_location: str


# Shared list so that the static generator and page generator can link together
RUN_HISTORY: dict[str, list[SvgPageContext]] = defaultdict(list)


def add_runmap_page(pageGenerator: generators.PagesGenerator):
    """Add srava page after Generators Finalized."""
    content = "Test Page"
    runmap_page = contents.Page(
        content,
        {
            "title": "Strava Runmap",
            "date": datetime.now(),
        },
    )
    pageGenerator.pages.append(runmap_page)
    print(RUN_HISTORY)


def add_run_images(staticGenerator: generators.StaticGenerator):
    """Add map SVGs after Static Generators Finalized.

    Actually calls the strava endpoint and generates all of the SVGs.
    The SVGs are then insterted in to a share context so that
        the page generator can access them.
    """
    strava_api = _strava_interface.StravaAPI(STRAVA_RUNMAP_SETTINGS)
    activities = strava_api.fetch_activities()
    for activity in activities:
        if not activity.map:
            continue
        activity_svg = _svg_interface.extract_svg_data(activity)
        static_file = contents.Static(
            _svg_interface.convert_to_svg(activity_svg),
            {"title": activity.name, "date": activity.start_date_local},
        )
        staticGenerator.staticfiles.append(static_file)

        RUN_HISTORY[str(activity.start_date_local.year)].append(
            SvgPageContext(
                display_date=activity.start_date_local,
                display_name=activity.name or "Untitled Run",
                svg_location=static_file.url,
            )
        )




def init_default_config(pelican):
    STRAVA_RUNMAP_SETTINGS.update(pelican.settings[STRAVA_RUNMAP_KEY])


def register():
    """Register article creation signals with pelican."""
    signals.initialized.connect(init_default_config)
    signals.page_generator_finalized.connect(add_runmap_page)
    signals.static_generator_finalized.connect(add_run_images)
