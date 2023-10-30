import dataclasses
import math

import polyline

from . import _strava_interface

EARTH_RADIUS_KM = 6378137.0

SVG_TEMPLATE = "\n".join(
    [
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" class="h-32">""",  # noqa: E501
        """ <g transform="translate(0,{height}) scale(1,-1)">""",
        """    <polyline points="{points}" fill="none" stroke="black"></polyline>""",
        "  </g>",
        "</svg>",
    ]
)


@dataclasses.dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


def y2lat(y):
    return math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_KM)) - math.pi / 2.0)


def lat2y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * EARTH_RADIUS_KM


def x2lng(x):
    return math.degrees(x / EARTH_RADIUS_KM)


def lon2x(lon):
    return math.radians(lon) * EARTH_RADIUS_KM


def convert_to_svg(activity_svg: ActivitySvg):
    # {% for coords in svg.points %}{{ coords.0 }},{{ coords.1 }} {% endfor %}
    points = " ".join(["{x},{y}" for (x, y) in activity_svg.points])

    return SVG_TEMPLATE.format(
        width=activity_svg.width, height=activity_svg.height, points=points
    )


def extract_svg_data(
    activity: _strava_interface.StravaRouteData,
    width: int = 50,
    height: int = 50,
    padding: int = 10,
) -> ActivitySvg | None:
    """Translate the geocoordinates of an activity to points for SVG drawing."""
    point_list = [
        list(coords) for coords in polyline.decode(activity.map.summary_polyline)
    ]
    if point_list:
        x_values: list[float] = []
        y_values: list[float] = []

        for lat, lon in point_list:
            # Use Mercator points so route doesn't look slightly off when flattened.
            projected_x = lon2x(lon)
            projected_y = lat2y(lat)
            x_values.append(projected_x)
            y_values.append(projected_y)

        max_x, max_y = max(x_values), max(y_values)
        min_x, min_y = min(x_values), min(y_values)
        map_width = max_x - min_x
        map_height = max_y - min_y
        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2
        scale = min(width / map_width, height / map_height)
        return ActivitySvg(
            points=[
                [
                    (x - center_x) * scale + width / 2,
                    (y - center_y) * scale + height / 2,
                ]
                for x, y in zip(x_values, y_values)
            ],
            width=width + padding,
            height=height + padding,
        )

    return None
