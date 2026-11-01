"""Layer 1 — deterministic tests for the tool.

No LLM, no network: the HTTP layer is replaced with fakes so the tests are
fast, free and give the same result every time.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from travel_planner.tools import weather_tool
from travel_planner.tools.weather_tool import get_weather_forecast

GEO = {"results": [{"name": "Graz", "country": "Austria", "latitude": 47.07,
                    "longitude": 15.44, "timezone": "Europe/Vienna"}]}
FORECAST = {
    "current_weather": {"temperature": 12.3, "windspeed": 8.0, "weathercode": 2, "time": "2026-11-10T12:00"},
    "daily": {
        "time": ["2026-11-10", "2026-11-11"],
        "weathercode": [2, 63],
        "temperature_2m_max": [14.0, 9.5],
        "temperature_2m_min": [6.0, 4.0],
        "precipitation_sum": [0.0, 7.2],
    },
}


def _response(payload, status=200):
    resp = MagicMock(status_code=status)
    resp.json.return_value = payload
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}")
    return resp


def _fake_get(url, params=None, timeout=None):
    return _response(GEO if "geocoding" in url else FORECAST)


@patch.object(weather_tool.requests, "get", side_effect=_fake_get)
def test_parses_live_api_response(_):
    result = get_weather_forecast("Graz", days=2)

    assert result["location"] == "Graz, Austria"
    assert result["source"] == "Open-Meteo Live API"
    assert result["current"]["temperature_c"] == 12.3
    assert [d["date"] for d in result["forecast"]] == ["2026-11-10", "2026-11-11"]
    assert result["forecast"][1]["condition"] == weather_tool.WMO_WEATHER_CODES[63]


@patch.object(weather_tool.requests, "get", side_effect=_fake_get)
def test_days_are_clamped_to_api_limits(mock_get):
    get_weather_forecast("Graz", days=99)
    forecast_call = mock_get.call_args_list[-1]
    assert forecast_call.kwargs["params"]["forecast_days"] == 7


@patch.object(weather_tool.requests, "get", side_effect=requests.ConnectionError("offline"))
def test_connection_error_propagates(_):
    with pytest.raises(requests.ConnectionError):
        get_weather_forecast("Vienna", days=2)


@patch.object(weather_tool.requests, "get", return_value=_response({}, status=500))
def test_server_error_propagates(_):
    with pytest.raises(requests.HTTPError):
        get_weather_forecast("Linz")


def _fake_get_empty_geo(url, params=None, timeout=None):
    return _response({"results": []} if "geocoding" in url else FORECAST)


@patch.object(weather_tool.requests, "get", side_effect=_fake_get_empty_geo)
def test_unknown_location_raises(_):
    with pytest.raises(ValueError, match="geocode"):
        get_weather_forecast("Atlantis")
