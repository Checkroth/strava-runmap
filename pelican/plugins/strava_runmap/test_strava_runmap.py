from datetime import datetime
from unittest import mock

import pytest
import zoneinfo

from . import _strava_interface, _svg_interface

MIN_ALLOWED_FLOAT_DIFF = 0.0001


class MockResponse:
    def __init__(self, response_data):
        """Just configure response data."""
        self.response_data = response_data

    def json(self):
        return self.response_data

    @property
    def ok(self):
        return True


@pytest.fixture
def strava_response():
    response_data = [
        {
            "resource_state": 2,
            "athlete": {"id": 241992, "resource_state": 1},
            "name": "Morning Walk",
            "distance": 3080.9,
            "moving_time": 1620,
            "elapsed_time": 1642,
            "total_elevation_gain": 40.9,
            "type": "Walk",
            "sport_type": "Walk",
            "id": 10128220001,
            "start_date": "2023-10-30T00:02:49Z",
            "start_date_local": "2023-10-30T09:02:49Z",
            "timezone": "(GMT+09:00) Asia/Tokyo",
            "utc_offset": 32400.0,
            "location_city": None,
            "location_state": None,
            "location_country": None,
            "achievement_count": 0,
            "kudos_count": 1,
            "comment_count": 0,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a10128220000",
                "summary_polyline": "er~hF}utzYm@`@URgCrAMHAFGFUNIDCA[RCFg@HQHK@Q@IEa@@QKGAYJQ?m@ESB[Ci@HYCu@Dk@AOGUHM@eAMC@g@SOMKC]SMCSSYSIKe@Kq@_@IAKBOCQIO?[BEES?}@Zs@N{A`@GAa@DMH_@Jy@Pa@NSBKGGUGq@GQAaB`@sEAQLu@Le@?a@Fe@AWBc@Ci@Fe@Cm@@YHGLE^@d@Kh@Sb@K~@i@fAc@v@c@^]x@_@`Am@l@[RED@ZW^ORQRIl@Q^E^@XEjAPXLn@Pr@Zr@Rf@XbAb@rAr@XJVLNBZP^JdAd@|Bb@RBRAf@F`@@RD~@D",  # noqa: E501
                "resource_state": 2,
            },
            "trainer": False,
            "commute": False,
            "manual": False,
            "private": False,
            "visibility": "everyone",
            "flagged": False,
            "gear_id": None,
            "start_latlng": [38.334597777575254, 140.85075683891773],
            "end_latlng": [38.334603141993284, 140.85117375478148],
            "average_speed": 1.902,
            "max_speed": 3.528,
            "average_cadence": 64.9,
            "has_heartrate": True,
            "average_heartrate": 103.1,
            "max_heartrate": 139.0,
            "heartrate_opt_out": False,
            "display_hide_heartrate_option": True,
            "elev_high": 100.9,
            "elev_low": 59.1,
            "upload_id": 10848968685,
            "upload_id_str": "10848968685",
            "external_id": "garmin_ping_302120476072",
            "from_accepted_tag": False,
            "pr_count": 0,
            "total_photo_count": 0,
            "has_kudoed": False,
        },
        {
            "resource_state": 2,
            "athlete": {"id": 100866000, "resource_state": 1},
            "name": "First fasting run 💀",
            "distance": 10520.3,
            "moving_time": 4351,
            "elapsed_time": 4351,
            "total_elevation_gain": 81.7,
            "type": "Run",
            "sport_type": "Run",
            "workout_type": 0,
            "id": 10121826000,
            "start_date": "2023-10-28T23:06:02Z",
            "start_date_local": "2023-10-29T08:06:02Z",
            "timezone": "(GMT+09:00) Asia/Tokyo",
            "utc_offset": 32400.0,
            "location_city": None,
            "location_state": None,
            "location_country": None,
            "achievement_count": 2,
            "kudos_count": 1,
            "comment_count": 0,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a10121826585",
                "summary_polyline": "_a~hFmjtzYO~@Uf@_@lAUdAS`@Yx@_@p@Sh@u@xAYZKRKV]p@SLCL?XGXKx@ChA@f@E`@Fr@A|@D^AVDh@CnAFxAAx@Dr@CbACD@d@D^CJW^AJFt@BHLJHPBtABd@Af@BbBE`B?lB@d@BJAVFj@Ev@Hz@@dBARDV@f@AzCJrF@vBAzADjAA`AEz@?TGn@[zAKb@]~@eArB{@~@c@l@_@Z}BhCa@ZOVOH]j@a@d@_C~BSDAVg@rAK\\In@OpBAnAH|@PfABt@N`AFr@CPGPc@Ze@Pm@b@kAn@uAbA{@h@e@\\{BzAg@`@UHMLc@VyAdAs@`@i@`@eAn@iATy@HcACi@@uAGOKES?IHq@Pi@Lk@@OPcAXoABa@Nm@h@iDh@aC\\iCPo@ZeBHoAB_ABS?WBc@CQAy@FwAAsBEMQgBWaBM{A[gBA]We@KeAWoAIu@Oy@QcBSqDGa@AmCBYDiCFo@@u@\\}AD[J[Jk@FgAJs@`@_CLcA@[HYLQFSDy@Hq@Lq@F_ALg@PwAHSTMDKFu@Mi@DM@YH]?GJm@JeADMLS@_@Ia@?]IaBE]UaAQwAW_AGk@W_AU{ASe@Ki@Ki@Ew@EQOSWiACi@?YKs@cAiCGk@Ia@SgBOk@CSO[Ke@Ca@FYEQKYC_@BkCNcB\\aCD_@BkAFy@BsAFaA?_BGkAM{AIe@S}AUeAUg@I]IOQo@Uq@CY_@u@O{@Yy@Qw@aAaCc@wAKk@]{@UkASk@AOIYAIa@kAYi@?IIOG]Sg@WaA}@yBm@aAiA_CAOBUDIf@Y`DaAHAVKb@GXKb@GjAc@r@O\\Oh@OxBaATK^Ir@_@hA_@^WLM^WbB}@RGl@EVQnAc@zBm@vDg@tA?\\CHBV@^GHEPALD^?LCv@Cp@D\\FlA?XDh@D@@@\\EfA@j@TnD?jALr@Dl@Lh@JPXlAf@v@bAjAd@^x@h@~@\\tBPZHb@Rh@Z^NLJNRRL|@t@n@V|@t@FLARMn@]jA[pBMrBMbAA|@I`AAtBKnBBr@?hAGzAIj@A~AFbAVjBCTBXADSDc@Aa@HKCq@JKAID",  # noqa: E501
                "resource_state": 2,
            },
            "trainer": False,
            "commute": False,
            "manual": False,
            "private": False,
            "visibility": "everyone",
            "flagged": False,
            "gear_id": None,
            "start_latlng": [38.33464412949979, 140.85069347172976],
            "end_latlng": [38.3346282877028, 140.85094241425395],
            "average_speed": 2.418,
            "max_speed": 3.63,
            "average_cadence": 75.6,
            "has_heartrate": True,
            "average_heartrate": 167.8,
            "max_heartrate": 188.0,
            "heartrate_opt_out": False,
            "display_hide_heartrate_option": True,
            "elev_high": 101.2,
            "elev_low": 58.1,
            "upload_id": 10842235490,
            "upload_id_str": "10842235490",
            "external_id": "garmin_ping_301936255068",
            "from_accepted_tag": False,
            "pr_count": 1,
            "total_photo_count": 0,
            "has_kudoed": False,
        },
    ]

    return MockResponse(response_data=response_data)


@pytest.fixture
def strava_activities() -> [_strava_interface.StravaRouteData]:
    return [
        _strava_interface.StravaRouteData(
            start_date_local=datetime(2023, 10, 30, 9, 2, 49),
            timezone=zoneinfo.ZoneInfo("Asia/Tokyo"),
            map=_strava_interface.MapData(
                id="a10128220000",
                summary_polyline="er~hF}utzYm@`@URgCrAMHAFGFUNIDCA[RCFg@HQHK@Q@IEa@@QKGAYJQ?m@ESB[Ci@HYCu@Dk@AOGUHM@eAMC@g@SOMKC]SMCSSYSIKe@Kq@_@IAKBOCQIO?[BEES?}@Zs@N{A`@GAa@DMH_@Jy@Pa@NSBKGGUGq@GQAaB`@sEAQLu@Le@?a@Fe@AWBc@Ci@Fe@Cm@@YHGLE^@d@Kh@Sb@K~@i@fAc@v@c@^]x@_@`Am@l@[RED@ZW^ORQRIl@Q^E^@XEjAPXLn@Pr@Zr@Rf@XbAb@rAr@XJVLNBZP^JdAd@|Bb@RBRAf@F`@@RD~@D",
                resource_state=2,
            ),
            name="Morning Walk",
            distance=3080.9,
            moving_time=1620,
        ),
        _strava_interface.StravaRouteData(
            start_date_local=datetime(2023, 10, 29, 8, 6, 2),
            timezone=zoneinfo.ZoneInfo("Asia/Tokyo"),
            map=_strava_interface.MapData(
                id="a10121826585",
                summary_polyline="_a~hFmjtzYO~@Uf@_@lAUdAS`@Yx@_@p@Sh@u@xAYZKRKV]p@SLCL?XGXKx@ChA@f@E`@Fr@A|@D^AVDh@CnAFxAAx@Dr@CbACD@d@D^CJW^AJFt@BHLJHPBtABd@Af@BbBE`B?lB@d@BJAVFj@Ev@Hz@@dBARDV@f@AzCJrF@vBAzADjAA`AEz@?TGn@[zAKb@]~@eArB{@~@c@l@_@Z}BhCa@ZOVOH]j@a@d@_C~BSDAVg@rAK\\In@OpBAnAH|@PfABt@N`AFr@CPGPc@Ze@Pm@b@kAn@uAbA{@h@e@\\{BzAg@`@UHMLc@VyAdAs@`@i@`@eAn@iATy@HcACi@@uAGOKES?IHq@Pi@Lk@@OPcAXoABa@Nm@h@iDh@aC\\iCPo@ZeBHoAB_ABS?WBc@CQAy@FwAAsBEMQgBWaBM{A[gBA]We@KeAWoAIu@Oy@QcBSqDGa@AmCBYDiCFo@@u@\\}AD[J[Jk@FgAJs@`@_CLcA@[HYLQFSDy@Hq@Lq@F_ALg@PwAHSTMDKFu@Mi@DM@YH]?GJm@JeADMLS@_@Ia@?]IaBE]UaAQwAW_AGk@W_AU{ASe@Ki@Ki@Ew@EQOSWiACi@?YKs@cAiCGk@Ia@SgBOk@CSO[Ke@Ca@FYEQKYC_@BkCNcB\\aCD_@BkAFy@BsAFaA?_BGkAM{AIe@S}AUeAUg@I]IOQo@Uq@CY_@u@O{@Yy@Qw@aAaCc@wAKk@]{@UkASk@AOIYAIa@kAYi@?IIOG]Sg@WaA}@yBm@aAiA_CAOBUDIf@Y`DaAHAVKb@GXKb@GjAc@r@O\\Oh@OxBaATK^Ir@_@hA_@^WLM^WbB}@RGl@EVQnAc@zBm@vDg@tA?\\CHBV@^GHEPALD^?LCv@Cp@D\\FlA?XDh@D@@@\\EfA@j@TnD?jALr@Dl@Lh@JPXlAf@v@bAjAd@^x@h@~@\\tBPZHb@Rh@Z^NLJNRRL|@t@n@V|@t@FLARMn@]jA[pBMrBMbAA|@I`AAtBKnBBr@?hAGzAIj@A~AFbAVjBCTBXADSDc@Aa@HKCq@JKAID",
                resource_state=2,
            ),
            name="First fasting run 💀",
            distance=10520.3,
            moving_time=4351,
        ),
    ]


@pytest.fixture
def mock_strava_api_get(monkeypatch, strava_response):
    import requests

    mock_get = mock.Mock()
    mock_get.side_effect = [strava_response, MockResponse(response_data=[])]
    monkeypatch.setattr(requests, "get", mock_get)
    return mock_get


@pytest.fixture
def mock_polyline_decode(monkeypatch, polyline_decode):
    import polyline

    mock_decode = mock.Mock()
    mock_decode.return_value = polyline_decode
    monkeypatch.setattr(polyline, "decode", mock_decode)

    return mock_decode


def test_strava_interface_valid(mock_strava_api_get, strava_activities):
    strava_api = _strava_interface.StravaAPI(
        client_settings={
            "CLIENT_ID": "123",
            "CLIENT_SECRET": "456",
            "REFRESH_TOKEN": "abcd1234",
        },
        auth_token="test-token123",
    )

    activities = strava_api.fetch_activities()

    mock_strava_api_get.assert_called()
    assert activities == strava_activities


@pytest.mark.parametrize(
    "polyline_decode,expect_svg_contents",
    [
        (
            [[0, 0], [1, 1]],
            [
                _svg_interface.ActivitySvg(
                    points=[[0.0012, 0.0], [49.9988, 50.0]], width=60, height=60
                ),
                _svg_interface.ActivitySvg(
                    points=[[0.0012, 0.0], [49.9988, 50.0]], width=60, height=60
                ),
            ],
        )
    ],
    ids=["COORDS_POPULATED"],
)
def test_strava_data_converts_to_svg_data(
    strava_activities, mock_polyline_decode, polyline_decode, expect_svg_contents
):
    # Arrange comes entirely from fixtures

    svg_data = [
        _svg_interface.extract_svg_data(activity) for activity in strava_activities
    ]

    for result, expect in zip(svg_data, expect_svg_contents):
        for result_points, expect_points in zip(result.points, expect.points):
            # assert expect_points == pytest.approx(result_points)
            for i, result_point in enumerate(result_points):
                # We don't care about the n-100th place,
                #     if it smells right its good enough
                diff = abs(result_point - expect_points[i])
                assert diff <= MIN_ALLOWED_FLOAT_DIFF

        assert result.width == expect.width
        assert result.height == expect.height


@pytest.mark.parametrize(
    "polyline_decode",
    [
        [],
    ],
    ids=["COORDS_EMPTY"],
)
def test_strava_data_turns_up_empty(
    strava_activities, polyline_decode, mock_polyline_decode
):
    svg_data = [
        _svg_interface.extract_svg_data(activity) for activity in strava_activities
    ]

    # Assert
    assert svg_data == [None, None]


@pytest.mark.skip("Not implemented")
def test_activity_svg_data_converts_to_svg(activity_svg_data):
    # Arrange
    # expect_svgs = """"""

    # Act
    svg_outputs = [
        _svg_interface.convert_to_svg(activity) for activity in strava_activities
    ]

    # Assert
    assert activity_svg_data == pytest.approx(svg_outputs)
