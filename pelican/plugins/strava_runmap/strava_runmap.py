from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
import logging

from pelican import contents, generators, signals

from . import _strava_interface, _svg_interface

logger = logging.getLogger(__name__)

STRAVA_RUNMAP_KEY = "STRAVA_RUNMAP"
PROJECT_LINK = "https://github.com/Checkroth/strava-runmap"
STRAVA_RUNMAP_SETTINGS = {
    "CLIENT_ID": "",
    "CLIENT_SECRET": "",
    "REFRESH_TOKEN": "",
    "ACTIVITIES_ENDPOINT": "",
    "STRAVA_DRY_RUN": "",
    "DATE_DISPLAY_FORMAT": "%Y-%m-%d",
}


@dataclass
class SvgPageContext:
    display_name: str
    display_date: date
    svg_content: str
    distance_display: str


# Shared list so that the static generator and page generator can link together
RUN_HISTORY: dict[str, list[SvgPageContext]] = defaultdict(list)


def _build_runmap_page(run_history: dict[str, list[SvgPageContext]]):
    """Use the collection of activity SVG data from strava to build a page's content.

    Activities will be grouped by year, and displayed in descending chronological order.
    Will ultimately look like the below, but is not done in an HTML template due to
        lack of being able to figure out how to inject that using pelican.

    <ul style="display: flex; flex-direction: column">
      {% for year in years %}
      <li>{{ year.display }}</li>
      <li>
        <ul style="display: flex; flex-direction: row; flex-wrap: wrap;">
          <li>
            {% for run in year %}
            <ul style="display: flex; flex-direction: column">
              <li>{{ run.title }}</li>
              <li>{{ run.svg }}</li>
              <li>{{ run.date }}</li>
            </ul>
            {% endfor %}
          </li>
        </ul>
      </li>
    </ul>

    """
    year_sections = []
    flex_style = "display: flex; list-style: none;"
    for year, svg_contexts in run_history.items():
        svg_sections = [
            "\n".join(
                [
                    '<li style="margin-top: 4rem;">',
                    f'<ul style="{flex_style} flex-direction: '
                    'column; max-width:10rem;">',
                    f"<li>{context.display_name}</li>",
                    f"<li>{context.svg_content}</li>",
                    f"<li>{context.display_date}</li>",
                    f"<li>{context.distance_display}<li>",
                    "</ul>",
                    "</li>",
                ]
            )
            for context in svg_contexts
        ]
        year_sections.append(
            "\n".join(
                [
                    f'<li style="text-align: center;"><h2>{year}</h2></li>',
                    "<li>",
                    f'<ul style="{flex_style}; flex-direction: row; flex-wrap: wrap">',
                    *svg_sections,
                    "</li>",
                ]
            )
        )

    return "\n".join(
        [
            f'<ul style="{flex_style} flex-direction: column;">',
            '<li style="text-align: center;"><h1>Maps of my Activities</h1></li>',
            f'<li style="text-align: center;"><p>Powered by <a href="{PROJECT_LINK}">'
            "strava-runmap for pelican</a>",
            *year_sections,
            "</ul>",
        ]
    )


def _create_run_images():
    """Add map SVGs after Static Generators Finalized.

    Actually calls the strava endpoint and generates all of the SVGs.
    The SVGs are then insterted in to a share context so that
        the page generator can access them.
    """
    logger.info("Connecting to Strava API")
    strava_api = _strava_interface.StravaAPI(STRAVA_RUNMAP_SETTINGS)
    logger.info("Fetching Strava activities")
    activities = strava_api.fetch_activities()
    run_history = defaultdict(list)
    for activity in activities:
        if not activity.map:
            # Not all strava activities have maps
            continue
        activity_svg = _svg_interface.extract_svg_data(activity)
        if not activity_svg:
            # Not all strava activity maps have polylines to svg-ize
            continue
        svg_content = _svg_interface.convert_to_svg(activity_svg)
        distance_display = f"{int(activity.distance)}m in {activity.moving_time // 60}"

        run_history[str(activity.start_date_local.year)].append(
            SvgPageContext(
                display_date=activity.start_date_local.strftime(
                    STRAVA_RUNMAP_SETTINGS["DATE_DISPLAY_FORMAT"]
                ),
                display_name=activity.name or "Untitled Run",
                svg_content=svg_content,
                distance_display=distance_display,
            )
        )
    logger.info("Strava Activities fetched")
    return run_history


def add_runmap_page(pageGenerator: generators.PagesGenerator):
    """Add srava page after Generators Finalized."""
    logger.info("Ading page for Run Maps")
    run_history = _create_run_images()
    content = _build_runmap_page(run_history)
    runmap_page = contents.Page(
        content,
        {
            "title": "Strava Runmap",
            "date": datetime.now(),
        },
    )
    pageGenerator.pages.append(runmap_page)


def init_default_config(pelican):
    STRAVA_RUNMAP_SETTINGS.update(pelican.settings[STRAVA_RUNMAP_KEY])


def register():
    """Register article creation signals with pelican."""
    signals.initialized.connect(init_default_config)
    signals.page_generator_finalized.connect(add_runmap_page)
