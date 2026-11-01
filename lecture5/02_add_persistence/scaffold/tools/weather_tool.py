"""Example tool for the persistence exercise.

Lecture 5 · Section 2: Add Persistence · SCAFFOLD
─────────────────────────────────────────────────
The tool implementation is complete — focus your work on agent.py.

You can replace this entire file with your own tool from Section 1.
The persistence pattern in agent.py works with ANY tool.

Key addition in this section: the tool can store data in session state
so the agent "remembers" things across turns.

How it works:
  - ADK injects a ToolContext object into any tool that declares it as a parameter.
  - tool_context.state is a dict shared across all turns in one session.
  - Write: tool_context.state["key"] = value
  - Read:  tool_context.state.get("key", default)

Raises on network or API errors — no offline fallback.
"""

import requests
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky ☀️", 1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
    45: "Fog 🌫️", 51: "Light drizzle 🌦️", 61: "Slight rain 🌧️", 63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️", 71: "Slight snow fall 🌨️", 80: "Slight rain showers 🌦️",
    95: "Thunderstorm ⛈️",
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
    """Get current weather and a multi-day forecast for a city.

    Saves the resolved location to session state so the agent can
    reference it in follow-up questions.

    Args:
        location: City name, e.g. "Vienna" or "Tokyo".
        days: Number of forecast days (1–7, default 3).
        tool_context: Injected by ADK. Gives access to session state.

    Returns:
        Dict with location, current conditions (temp, wind, condition),
        and a daily forecast list.
    """
    days = max(1, min(days, 7))
    geo = _get_coordinates(location)

    if tool_context is not None:
        tool_context.state["last_location"] = geo["name"]  # ← persistence magic

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
