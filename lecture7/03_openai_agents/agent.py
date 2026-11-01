"""Weather Agent — OpenAI Agents SDK Implementation.

Lecture 7 · FH Technikum Wien — Deep Learning Engineering / AI Agents Course.

Demonstrates:
- OpenAI Agents SDK primitives: Agent, Runner, @function_tool
- Async execution model with Runner.run()
- Built-in tool-call loop and tracing

NOTE: This implementation requires an OPENAI_API_KEY (not GEMINI_API_KEY)
      because the OpenAI Agents SDK natively targets OpenAI models.

Run:
    cd lecture7/03_openai_agents
    python agent.py
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

from tools.weather_tool import get_weather_forecast as _fetch_weather


# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()

# ── Model selection ───────────────────────────────────────────────────────────
# The OpenAI Agents SDK reads OPENAI_API_KEY and OPENAI_BASE_URL automatically.
# Set USE_LOCAL_LLM=true to point the SDK at the FH Lion endpoint.

_USE_LOCAL = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
_MODEL = "Qwen/Qwen3.6-35B-A3B" if _USE_LOCAL else "gpt-4o"


# ── Tool Definition ───────────────────────────────────────────────────────────

@function_tool
def get_weather_forecast(location: str, days: int = 3) -> str:
    """Retrieve the current weather and a multi-day forecast for a location.

    Args:
        location: City or region name, e.g. 'Vienna', 'Berlin', 'New York'.
        days: Number of forecast days (1-7, default 3).
    """
    result = _fetch_weather(location, days)
    return json.dumps(result, indent=2)


# ── Agent Definition ──────────────────────────────────────────────────────────

weather_agent = Agent(
    name="Weather Assistant",
    instructions=(
        "You are a friendly Meteorological AI Assistant created for "
        "FH Technikum Wien students.\n\n"
        "ALWAYS use the `get_weather_forecast` tool when a user asks about "
        "weather. Default to 3 forecast days if not specified.\n"
        "Present results clearly: location, current conditions, daily "
        "forecast table, and practical advice (umbrella, jacket, etc.)."
    ),
    tools=[get_weather_forecast],
    model=_MODEL,
)


# ── Interactive CLI Loop ─────────────────────────────────────────────────────

async def run_agent(user_input: str) -> str:
    """Run the agent on a single user query and return the response."""
    result = await Runner.run(weather_agent, input=user_input)
    return result.final_output


def main():
    print("=" * 60)
    _model_name = "Qwen3.6-35B-A3B (Lion)" if _USE_LOCAL else "GPT-4o"
    print("🌦️  Weather Agent — OpenAI Agents SDK")
    print(f"   Model: {_model_name}  |  Framework: OpenAI Agents SDK")
    print("=" * 60)
    print("Type your question (or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("[user]: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        response = asyncio.run(run_agent(user_input))
        print(f"\n[agent]: {response}\n")


if __name__ == "__main__":
    main()
