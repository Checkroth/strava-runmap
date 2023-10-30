"""Interface directly with strava and get rid of the stuff we don't care about.

https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
"""
import dataclasses
from datetime import datetime

import requests
import zoneinfo

STRAVA_DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclasses.dataclass
class AthleteData:
    id: int
    resource_state: int


@dataclasses.dataclass
class MapData:
    id: str
    summary_polyline: str
    resource_state: int


@dataclasses.dataclass
class StravaRouteData:
    """Represents the actual API response from Strava.

    The fields we don't actually use are commented-out, but exist in Strava.
    To start making use of them, simply uncomment the field and fix tests.

    https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    """

    # name: str
    # athlete: AthleteData
    # distance: Decimal
    # moving_time: int
    # elapsed_time: int
    # total_elevation_gain: int
    # type: str
    # sport_type: str
    # workout_type: None
    # id: id
    # external_id: str
    # upload_id: int
    # start_date: datetime
    start_date_local: datetime
    timezone: zoneinfo.ZoneInfo
    # utc_offset: int
    # start_latlng: None
    # end_latlng: None
    # location_city: None
    # location_state: None
    # location_country: str
    # achievement_count: int
    # kudos_count: int
    # comment_count: int
    # athlete_count: int<
    # photo_count: int
    map: MapData
    # trainer: bool
    # commute: bool
    # manual: bool
    # private: bool
    # flagged: bool
    # gear_id: str
    # from_accepted_tag: bool
    # average_speed: Decimal
    # max_speed: int
    # average_cadence: Decimal
    # average_watts: Decimal
    # weighted_average_watts: int
    # kilojoules: Decimal
    # device_watts: bool
    # has_heartrate: bool
    # average_heartrate: Decimal
    # max_heartrate: int
    # max_watts: int
    # pr_count: int
    # total_photo_count: int
    # has_kudoed: bool
    # suffer_score: int

    @classmethod
    def from_strava_data(cls, strava_response: dict):
        # athlete_data = strava_response.pop("athlete")
        map_data = strava_response.pop("map")
        try:
            # Strava gives us timezones in the form of `(GMT+09:00) Asia/Tokyo`, but
            #     zoneinfo expects just the latter named part.
            timezone = strava_response["timezone"].split()[1]
        except (AttributeError, IndexError):
            timezone = ""
        return cls(
            start_date_local=datetime.strptime(
                strava_response["start_date_local"], STRAVA_DT_FORMAT
            ),
            timezone=zoneinfo.ZoneInfo(timezone),
            map=MapData(**map_data),
        )


@dataclasses.dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


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
            if response.ok:
                routes.extend(
                    [
                        StravaRouteData.from_strava_data(route)
                        for route in response.json()
                    ]
                )
            return req_page + 1

        prev_len = -1  # Anything other than 0 to kick off the loop.
        page = 1
        while prev_len != len(routes):
            prev_len = len(routes)
            page = _fetch_from_strava(page)
        return routes
