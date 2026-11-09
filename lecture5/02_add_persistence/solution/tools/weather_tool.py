"""Weather tool with session-state persistence.

Lecture 5 · Section 2: Add Persistence · SOLUTION
─────────────────────────────────────────────────
Key addition vs. Section 1: the tool accepts `tool_context: ToolContext` and
writes the resolved location into session state so the agent can reference it
in follow-up questions without the user repeating themselves.

Raises on network or API errors — no offline fallback.
"""

import requests
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky ☀️", 1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
    45: "Fog 🌫️", 48: "Depositing rime fog 🌫️", 51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️", 55: "Dense drizzle 🌧️", 61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️", 65: "Heavy rain 🌧️", 71: "Slight snow fall 🌨️",
    73: "Moderate snow fall 🌨️", 75: "Heavy snow fall ❄️",
    80: "Slight rain showers 🌦️", 81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️", 95: "Thunderstorm ⛈️",
}


def _get_coordinates(location: str) -> Dict[str, Any]:
    """Geocode a location name to latitude/longitude using Open-Meteo."""
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=5,
    )
    resp.raise_for_status()
    results = (resp.json() or {}).get("results") or []
    if not results:
        raise ValueError(f"Could not geocode location: {location!r}")
    r = results[0]
    return {
        "name": r["name"],
        "country": r.get("country", ""),
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "timezone": r.get("timezone", "UTC"),
    }


def get_weather_forecast(
    location: str,
    days: int = 3,
    tool_context: ToolContext = None,   # ADK injects this — do NOT pass it yourself
) -> Dict[str, Any]:
    """Retrieve current weather and a multi-day forecast for a location.

    Stores the resolved city name in session state under "last_location"
    so the agent can use it in follow-up questions.

    Args:
        location: City or region name (e.g. "Vienna", "New York").
        days: Number of forecast days (1–7, default 3).
        tool_context: Injected by ADK — provides read/write access to session state.

    Returns:
        Dict with location, current conditions, and daily forecast.
    """
    days = max(1, min(days, 7))
    geo = _get_coordinates(location)

    if tool_context is not None:
        tool_context.state["last_location"] = geo["name"]

    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": geo["latitude"], "longitude": geo["longitude"],
            "current_weather": "true",
            "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": geo.get("timezone", "auto"),
            "forecast_days": days,
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current_weather", {})
    daily = data.get("daily", {})
    daily_forecasts = [
        {
            "date": daily["time"][i],
            "max_temp_c": daily["temperature_2m_max"][i],
            "min_temp_c": daily["temperature_2m_min"][i],
            "condition": WMO_WEATHER_CODES.get(daily["weathercode"][i], "Clear"),
            "precipitation_mm": daily["precipitation_sum"][i],
        }
        for i in range(len(daily.get("time", [])))
    ]
    return {
        "location": f"{geo['name']}, {geo['country']}",
        "current": {
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "condition": WMO_WEATHER_CODES.get(current.get("weathercode", 0), "Unknown"),
        },
        "forecast": daily_forecasts,
        "source": "Open-Meteo Live API",
    }
