"""Specialists for the A2A section.

Lecture 5 · Section 4: A2A Protocol · SOLUTION
──────────────────────────────────────────────
Same two agents as Section 3, with one upgrade: weather_agent no longer
imports the Python weather function directly — it reaches it via an MCP
server (`mcp_weather_server.py`) spawned as a stdio subprocess.

So the full picture, once everything runs, is:

    adk web ──A2A──► weather_server.py ──MCP──► mcp_weather_server.py ──HTTP──► Open-Meteo
            ──A2A──► advisor_server.py   (no tools — reasoning only)

A2A moves tasks between agents; MCP moves tool calls between an agent and
an external capability provider.
"""

import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

_HERE = Path(__file__).resolve().parent


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"


_MODEL = _get_model()


# ── MCP toolset — spawns mcp_weather_server.py over stdio ─────────────────────
# The subprocess is created lazily on the first tool call, so importing this
# module is cheap. `cwd` is pinned so the server can `import tools.weather_tool`
# regardless of where the parent A2A server was launched from.

weather_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["mcp_weather_server.py"],
            cwd=str(_HERE),
        ),
        timeout=10.0,  # geocoding + forecast → ~2 outbound HTTP calls
    ),
)


weather_agent = Agent(
    name="weather_agent",
    model=_MODEL,
    description="Fetches live weather and a daily forecast for a city (via MCP).",
    instruction="""You are a weather data specialist.
ALWAYS call get_weather_forecast — never guess conditions.
Return the resolved location and, for each day, the ISO date, condition and min/max °C.
""",
    tools=[weather_mcp],
)


activity_advisor = Agent(
    name="activity_advisor",
    model=_MODEL,
    description="Suggests activities for a destination given a weather summary.",
    instruction="""You are a local activity advisor for students on a budget.
Given a destination and a per-day weather summary, suggest 2-4 activities per day.
Prefer indoor options on rainy or stormy days. Give a rough cost in EUR for each.
""",
)
