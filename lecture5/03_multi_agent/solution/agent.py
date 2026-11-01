"""Travel Planner — Google ADK Multi-Agent System.

Lecture 5 · Section 3: Multi-Agent with sub_agents · SOLUTION
─────────────────────────────────────────────────────────────
Demonstrates:
- Multi-agent orchestration via sub_agents=[...]
- Tool-calling sub-agent (weather_agent uses Open-Meteo API)
- Reasoning-only sub-agent (activity_advisor — pure LLM knowledge, no tools)
- Root agent synthesises both responses into one travel briefing

The user always talks to root_agent only; it delegates internally.
"""

import os
from google.adk.agents import Agent
from .tools.weather_tool import get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()


# ── Sub-Agent 1: Weather Specialist ───────────────────────────────────────────
# Same tool-calling pattern as Section 1, now running as a sub-agent.

weather_agent = Agent(
    name="weather_agent",
    model=_MODEL,
    instruction="""You are a weather data specialist.
ALWAYS call get_weather_forecast for any location question — never guess conditions.
Return: current temperature (°C), condition, wind speed, and a clean daily forecast table.
Close with one practical tip (umbrella, sunscreen, extra layer, etc.).
""",
    tools=[get_weather_forecast],
)


# ── Sub-Agent 2: Activity Advisor ─────────────────────────────────────────────
# No tools — specialisation comes entirely from the instruction.

activity_advisor = Agent(
    name="activity_advisor",
    model=_MODEL,
    instruction="""You are a local activity advisor for day-trippers and students.
Given a destination and a weather summary, suggest exactly 4-5 specific activities
with one-line descriptions. Always include a mix of outdoor and indoor options so the
plan works regardless of the actual weather. Keep suggestions budget-friendly.
""",
)


# ── Root Agent: Travel Planner Orchestrator ────────────────────────────────────
# Orchestrates sub-agents; never calls tools directly.

root_agent = Agent(
    name="travel_planner",
    model=_MODEL,
    instruction="""You are a Travel Planner assistant for FH Technikum Wien students.

For trip or destination questions:
1. Delegate to weather_agent to fetch the current forecast for the destination.
2. Pass the location and weather summary to activity_advisor for tailored activity ideas.
3. Combine both responses into one concise travel briefing for the student.

For weather-only questions: use weather_agent alone.
For activity-only questions: use activity_advisor directly.
Be friendly, concise, and practical.
""",
    sub_agents=[weather_agent, activity_advisor],
)
