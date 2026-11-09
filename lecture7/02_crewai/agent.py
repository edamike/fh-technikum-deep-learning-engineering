"""Weather Agent — CrewAI Implementation.

Lecture 7 · FH Technikum Wien — Deep Learning Engineering / AI Agents Course.

Demonstrates:
- CrewAI's Agent / Task / Crew abstraction
- Custom tool via the `@tool` decorator from `crewai.tools`
- Using Google Gemini via CrewAI's built-in LiteLLM integration

Run:
    cd lecture7/02_crewai
    python agent.py
"""

import json
import os

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool

from tools.weather_tool import get_weather_forecast as _fetch_weather


# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()

# ── Model selection ───────────────────────────────────────────────────────────
# CrewAI uses LiteLLM under the hood, so both Gemini and OpenAI-compatible
# endpoints work via the same model-string convention.
# Set USE_LOCAL_LLM=true + OPENAI_API_KEY + OPENAI_BASE_URL to use FH Lion.

_USE_LOCAL = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
_LLM = "openai/Qwen/Qwen3.6-35B-A3B" if _USE_LOCAL else "gemini/gemini-3.8-flash"


# ── Tool Definition ───────────────────────────────────────────────────────────

@tool
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
    role="Meteorological AI Assistant",
    goal=(
        "Provide accurate, well-formatted weather forecasts for any location "
        "worldwide, including practical clothing and activity advice."
    ),
    backstory=(
        "You are a weather expert assistant created for FH Technikum Wien "
        "students. You always use the get_weather_forecast tool to fetch live "
        "data before answering weather questions."
    ),
    tools=[get_weather_forecast],
    llm=_LLM,
    verbose=True,
)


# ── Task Definition ───────────────────────────────────────────────────────────

def create_forecast_task(user_query: str) -> Task:
    """Create a forecast task from a user query."""
    return Task(
        description=(
            f"Answer the following weather question from a student:\n\n"
            f'"{user_query}"\n\n'
            f"Use the get_weather_forecast tool. If no days are specified, "
            f"default to 3. Present: location, current conditions, daily "
            f"forecast, and practical advice (umbrella, jacket, etc.)."
        ),
        expected_output=(
            "A clear weather report with current conditions, daily forecast "
            "table, and actionable advice."
        ),
        agent=weather_agent,
    )


# ── Interactive CLI Loop ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    _model_name = "Qwen3.6-35B-A3B (Lion)" if _USE_LOCAL else "Gemini 3.8 Flash"
    print("🌦️  Weather Agent — CrewAI")
    print(f"   Model: {_model_name}  |  Framework: CrewAI")
    print("=" * 60)
    print("Type your question (or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("[user]: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        task = create_forecast_task(user_input)
        crew = Crew(
            agents=[weather_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        print(f"\n[agent]: {result.raw}\n")


if __name__ == "__main__":
    main()
