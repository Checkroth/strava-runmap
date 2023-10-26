"""
Module to interface directly with strava and get rid of the stuff we don't care about.
https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
"""
import math
import dataclasses
from decimal import Decimal
from datetime import datetime

import requests


@dataclasses.dataclass
class AthleteData:
    id: int
    resource_state: int


@dataclasses.dataclass
class MapData:
    id: str
    summary_polyline: None
    resource_state: int


@dataclasses.dataclass
class StravaRouteData:
    name: str
    athlete: AthleteData
    distance: Decimal
    moving_time: int
    elapsed_time: int
    total_elevation_gain: int
    type: str
    sport_type: str
    workout_type: None
    id: id
    external_id: str
    upload_id: int
    start_date: datetime
    start_date_local: datetime
    timezone: str
    utc_offset: int
    start_latlng: None
    end_latlng: None
    location_city: None
    location_state: None
    location_country: str
    achievement_count: int
    kudos_count: int
    comment_count: int
    athlete_count: int
    photo_count: int
    map: MapData
    trainer: bool
    commute: bool
    manual: bool
    private: bool
    flagged: bool
    gear_id: str
    from_accepted_tag: bool
    average_speed: Decimal
    max_speed: int
    average_cadence: Decimal
    average_watts: Decimal
    weighted_average_watts: int
    kilojoules: Decimal
    device_watts: bool
    has_heartrate: bool
    average_heartrate: Decimal
    max_heartrate: int
    max_watts: int
    pr_count: int
    total_photo_count: int
    has_kudoed: bool
    suffer_score: int

    @classmethod
    def from_strava_data(cls, strava_response: dict):
        athlete_data = strava_response.pop("athlete")
        map_data = strava_response.pop("map")
        return cls(
            athlete=AthleteData(**athlete_data),
            map=MapData(**map_data),
            **strava_response,
        )


@dataclasses.dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


EARTH_RADIUS_KM = 6378137.0


# TODO:: Move math out of here

def y2lat(y):
    return math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_KM)) - math.pi / 2.0)


def lat2y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * EARTH_RADIUS_KM


def x2lng(x):
    return math.degrees(x / EARTH_RADIUS_KM)


def lon2x(lon):
    return math.radians(lon) * EARTH_RADIUS_KM
def convert_to_svg(activity: StravaRouteData, width: int = 50, height: int = 50, padding: int = 10) -> ActivitySvg | None:
    """
    Translate the geocoordinates of an activity to points that can be used when drawing a svg.
    """
    point_list = get_point_list(activity)
    if point_list:
        x_values: list[float] = []
        y_values: list[float] = []

        for lat, lon in point_list:
            # Use Mercator points so route doesn't look slightly off when flattened.
            projected_x = gis_queries.lon2x(lon)
            projected_y = gis_queries.lat2y(lat)
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
                [(x - center_x) * scale + width / 2, (y - center_y) * scale + height / 2]
                for x, y in zip(x_values, y_values)
            ],
            width=width + padding,
            height=height + padding,
        )

    return None

class StravaAPI:
    activities_endpoint: str
    auth_token: str

    def __init__(self, auth_token: str | None):
        if not auth_token:
            auth_token = self.get_auth_token()
        self.auth_token = auth_token
        self.activities_endpoint = self.fetch_activities_endpoint()

    @classmethod
    def get_auth_token(cls) -> str:
        # TODO:: actually get auth token
        return ""

    @classmethod
    def fetch_activities_endpoint(cls) -> str:
        # TODO:: implement configurability
        return "https://www.strava.com/api/v3/athlete/activities"

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"}

    def fetch_activities(self) -> list[StravaRouteData]:
        # Fetch a
        routes = []

        def _fetch_from_strava(req_page: int = 1):
            run_url = f"{self.activities_endpoint}?page={req_page}"
            response = requests.get(run_url, headers=self.auth_headers)
            if response.status_code == 200:
                routes.append(StravaRouteData.from_strava_data(response.json()))
            return req_page + 1

        prev_len = -1  # Anything other than 0 to kick off the loop.
        page = 1
        while prev_len != len(routes):
            page = _fetch_from_strava(page)
        return routes
