"""Interface directly with strava and get rid of the stuff we don't care about.

https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
"""

import dataclasses
from datetime import datetime
from decimal import Decimal

import requests
import zoneinfo

STRAVA_DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_ACTIVITIES_ENDPOINT = "https://www.strava.com/api/v3/activities"
DEFAULT_AUTH_ENDPOINT = "https://www.strava.com/oauth/token"


class StravaAuthorizationError(Exception): ...


class StravaAPIMisconfigured(Exception):
    def __init__(self):
        super().__init__(
            "Missing one of CLIENT_ID, CLIENT_SECRET, "
            "and AUTH_CODE in the STRAVA_RUNMAP pelican configuration."
        )


class StravaAPIError(Exception):
    def __init__(self, message: str):
        super().__init__(
            f"Encountered an error trying to communicate with Strava: {message}"
        )


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

    name: str
    # athlete: AthleteData
    distance: Decimal
    moving_time: int
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
            name=strava_response["name"],
            distance=strava_response["distance"],
            moving_time=strava_response["moving_time"],
        )


@dataclasses.dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


class StravaAPI:
    activities_endpoint: str
    stored_auth_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    dry_run: bool

    def __init__(self, client_settings: dict[str, str], auth_token: str | None = None):
        self.client_id = client_settings["CLIENT_ID"]
        self.client_secret = client_settings["CLIENT_SECRET"]
        self.refresh_token = client_settings["REFRESH_TOKEN"]
        self.stored_auth_token = auth_token
        self.activities_endpoint = (
            client_settings.get("ACTIVITIES_ENDPOINT") or DEFAULT_ACTIVITIES_ENDPOINT
        )
        self.dry_run = bool(client_settings.get("STRAVA_DRY_RUN"))

    def get_auth_token(self) -> str:
        if self.stored_auth_token:
            return self.stored_auth_token

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise StravaAPIMisconfigured()

        resp = requests.post(
            DEFAULT_AUTH_ENDPOINT,
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if not resp.ok:
            raise StravaAuthorizationError(resp.content)

        access_token = resp.json().get("access_token")
        self.stored_auth_token = access_token
        return access_token

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.get_auth_token()}"}

    def fetch_activities(self) -> list[StravaRouteData]:
        routes = []
        if self.dry_run:
            return routes

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
            else:
                raise StravaAPIError(response.content)
            return req_page + 1

        prev_len = -1  # Anything other than 0 to kick off the loop.
        page = 1
        while prev_len != len(routes):
            prev_len = len(routes)
            page = _fetch_from_strava(page)
        return routes
