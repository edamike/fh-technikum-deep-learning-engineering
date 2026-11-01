"""Example tool — Open-Meteo weather API.

Lecture 5 · Section 1: Single Agent · SCAFFOLD
─────────────────────────────────────────────
This file shows the STRUCTURE of an ADK tool.
You can keep this weather example or replace it with any domain you like:

  Ideas:
    - Currency converter (exchange rate API)
    - Wikipedia summary (requests + Wikipedia REST API)
    - Current time / timezone lookup
    - Random joke / quote API
    - Simple calculator (no external API needed)
    - News headlines (any free news API)

Whatever you choose, the pattern is always the same:
  1. Write a plain Python function with typed parameters and a return type.
  2. Write a clear docstring — the LLM reads it to decide when to call the tool.
  3. Register it in Agent(tools=[your_function]).

Let the function raise on network / API errors — the agent framework will
surface them. Do NOT swallow errors with a silent fallback.

─────────────────────────────────────────────
TODO: Implement the two functions below.
      Or replace them entirely with your own tool.

Test the raw APIs in your browser first:
  Geocoding: https://geocoding-api.open-meteo.com/v1/search?name=Vienna&count=1
  Forecast:  https://api.open-meteo.com/v1/forecast?latitude=48.2&longitude=16.4&current_weather=true
"""

import requests
from typing import Any, Dict

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 51: "Light drizzle", 61: "Slight rain", 63: "Moderate rain",
    65: "Heavy rain", 71: "Slight snow", 80: "Slight showers", 95: "Thunderstorm",
}


def _get_coordinates(location: str) -> Dict[str, Any]:
    """Geocode a city name to lat/lon via Open-Meteo.

    TODO:
      1. Call https://geocoding-api.open-meteo.com/v1/search
         with params: name=location, count=1, language="en", format="json"
      2. Return a dict with name, country, latitude, longitude, timezone.
      3. Raise ValueError when no match is returned.
    """
    raise NotImplementedError("TODO: implement geocoding call")


def get_weather_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """Get current weather and a multi-day forecast for a city.

    The docstring is what the LLM sees — write it clearly!

    Args:
        location: City name, e.g. "Vienna" or "Tokyo".
        days: Number of forecast days (1–7).

    Returns:
        Dict with location, current conditions, and daily forecast.

    TODO:
      1. Clamp days to [1, 7].
      2. Call _get_coordinates(location).
      3. Call https://api.open-meteo.com/v1/forecast
         with latitude, longitude, current_weather=true,
         daily=[weathercode, temperature_2m_max, temperature_2m_min, precipitation_sum],
         timezone, forecast_days.
      4. Return structured data. Use WMO_WEATHER_CODES for condition strings.
      5. Call response.raise_for_status() — let network/API errors bubble up.
    """
    days = max(1, min(days, 7))
    raise NotImplementedError("TODO: implement the real API call")
