"""Weather Agent — Google ADK Single-Agent Example.

Lecture 5 · Section 1: Single Agent · SOLUTION
─────────────────────────────────────────────
Demonstrates:
- Defining an ADK Agent with a registered Python tool (Level 3: Tool Calling)
- Tool description drives LLM decision-making (ReAct pattern)
- Separation of concerns: LLM reasons, tool fetches data
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


root_agent = Agent(
    name="weather_agent",
    model=_MODEL,
    description="A weather agent that provides current conditions and forecasts.",
    instruction="""You are a professional weather assistant.

ALWAYS call get_weather_forecast for any location question — never guess conditions.

Format your answer as:
1. Current conditions (temperature, condition, wind speed)
2. A short daily forecast table (date | condition | min/max °C)
3. One practical tip (e.g. bring an umbrella, wear sunscreen, pack a warm layer)

Be concise and friendly.
""",
    tools=[get_weather_forecast],
)
