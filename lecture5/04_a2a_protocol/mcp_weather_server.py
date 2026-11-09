"""Weather MCP server — exposes `get_weather_forecast` over MCP (stdio).

Lecture 5 · Section 4: A2A Protocol · SOLUTION
──────────────────────────────────────────────
The weather A2A specialist (weather_server.py) does not import the Python
weather function directly. Instead it spawns this script as a subprocess
and talks to it over the Model Context Protocol (stdio transport). This
layered setup demonstrates the two complementary standards:

    adk web  ──A2A──►  weather_server.py  ──MCP──►  mcp_weather_server.py
   (agents talking to agents)      (agents talking to tools)

A2A moves tasks between agents; MCP moves tool calls between an agent and
an external capability provider. The two protocols stack naturally.

This file is run automatically by the McpToolset in `specialists.py` — you
do not launch it yourself. For debugging you can run it directly:

    python mcp_weather_server.py
    # it will wait for MCP JSON-RPC frames on stdin
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from tools.weather_tool import get_weather_forecast as _fetch_weather

mcp = FastMCP("weather")


@mcp.tool()
def get_weather_forecast(location: str, days: int = 3) -> dict[str, Any]:
    """Retrieve current weather and a multi-day forecast for a location.

    Args:
        location: City or region name (e.g. "Vienna", "Berlin", "Tokyo").
        days: Number of forecast days (1-7, default 3).

    Returns:
        Dict with resolved location, current conditions, and daily forecast.
    """
    return _fetch_weather(location, days)


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
