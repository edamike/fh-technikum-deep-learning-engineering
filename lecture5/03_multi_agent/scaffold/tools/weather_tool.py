"""Weather tool — complete implementation (same as Section 2 solution).

Lecture 5 · Section 3: Multi-Agent · SCAFFOLD
────────────────────────────────────────────
This file is provided as-is. Focus your TODOs on agent.py.

Raises on network or API errors — no offline fallback.
"""

import requests
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    51: "Light drizzle 🌦️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow fall 🌨️",
    80: "Slight rain showers 🌦️",
    95: "Thunderstorm ⛈️",
}


def _get_coordinates(location: str) -> Dict[str, Any]:
    """Geocode a location name to latitude/longitude using Open-Meteo."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    results = (response.json() or {}).get("results") or []
    if not results:
        raise ValueError(f"Could not geocode location: {location!r}")
    r = results[0]
    return {
        "name": r.get("name"),
        "country": r.get("country", ""),
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "timezone": r.get("timezone", "UTC"),
    }


def get_weather_forecast(
    location: str,
    days: int = 3,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Retrieve current weather and a multi-day forecast for a location.

    Args:
        location: City or region name (e.g. "Vienna", "New York").
        days: Number of forecast days (1–7, default 3).
        tool_context: Injected by ADK — provides access to session state.

    Returns:
        Structured weather dict with current conditions and daily forecast.
    """
    days = max(1, min(days, 7))
    geo = _get_coordinates(location)

    if tool_context is not None:
        tool_context.state["last_location"] = geo["name"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "current_weather": "true",
        "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": geo.get("timezone", "auto"),
        "forecast_days": days,
    }
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    current = data.get("current_weather", {})
    daily = data.get("daily", {})

    times = daily.get("time", [])
    daily_forecasts = []
    for i in range(len(times)):
        wcode = daily.get("weathercode", [])[i] if i < len(daily.get("weathercode", [])) else 0
        daily_forecasts.append({
            "date": times[i],
            "max_temp_c": daily.get("temperature_2m_max", [None])[i],
            "min_temp_c": daily.get("temperature_2m_min", [None])[i],
            "condition": WMO_WEATHER_CODES.get(wcode, "Clear"),
            "precipitation_mm": daily.get("precipitation_sum", [0.0])[i],
        })

    return {
        "location": f"{geo['name']}, {geo['country']}",
        "current": {
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "condition": WMO_WEATHER_CODES.get(current.get("weathercode", 0), "Unknown"),
            "time": current.get("time"),
        },
        "forecast": daily_forecasts,
        "source": "Open-Meteo Live API",
    }
