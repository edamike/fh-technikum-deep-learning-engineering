"""Shared Weather Utilities — Open-Meteo API Client.

Used by all three framework implementations (LangChain, CrewAI, OpenAI Agents SDK)
so that the weather-fetching logic is identical across demos. The function
raises on network or API errors — there is no offline fallback.
"""

import requests
from typing import Any, Dict


# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow fall 🌨️",
    73: "Moderate snow fall 🌨️",
    75: "Heavy snow fall ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
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


def get_weather_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """Retrieve current weather and a multi-day forecast for any location.

    Args:
        location: City or region name (e.g. 'Vienna', 'Berlin', 'New York').
        days: Number of forecast days (1–7, default 3).

    Returns:
        Dict with current conditions, daily forecasts, and metadata.
    """
    days = max(1, min(days, 7))
    geo = _get_coordinates(location)

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
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    codes = daily.get("weathercode", [])
    precips = daily.get("precipitation_sum", [])

    daily_forecasts = [
        {
            "date": times[i],
            "max_temp_c": max_temps[i] if i < len(max_temps) else None,
            "min_temp_c": min_temps[i] if i < len(min_temps) else None,
            "condition": WMO_WEATHER_CODES.get(codes[i] if i < len(codes) else 0, "Clear"),
            "precipitation_mm": precips[i] if i < len(precips) else 0.0,
        }
        for i in range(len(times))
    ]

    return {
        "location": f"{geo['name']}, {geo['country']}",
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "current": {
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "condition": WMO_WEATHER_CODES.get(current.get("weathercode", 0), "Unknown"),
            "time": current.get("time"),
        },
        "forecast": daily_forecasts,
        "source": "Open-Meteo Live API",
    }
