"""Travel Planner — VULNERABLE version.

Lecture 6 · Section 3: Security · SCAFFOLD
──────────────────────────────────────────
The structured travel planner from Sections 1 + 2, extended with a reviews tool
that returns UNTRUSTED user-generated content (tools/reviews_tool.py).
This version has no defences. Your job:

  1. Attack it    (see README — indirect and direct prompt injection)
  2. Defend it    implement guardrails.py and register the callbacks below (TODO A, B)
  3. Harden it    tell the agents that tool output is data, not instructions (TODO C)
  4. Prove it     add attack cases to evals/ (see README)

Replace the travel planner with your own agent if you like — the attack works
against any agent that reads untrusted text.
"""

import os
import re
from typing import Literal, Optional

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field, field_validator

from .guardrails import block_prompt_injection, sanitize_reviews  # noqa: F401 — used once TODO A/B are done
from .tools import get_local_reviews, get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()


# ── Output schema (unchanged from Section 1) ──────────────────────────────────

ActivityCategory = Literal["outdoor", "indoor", "food", "culture", "nightlife"]


class Activity(BaseModel):
    name: str = Field(description="Short name of the activity, e.g. 'Schönbrunn Palace'")
    category: ActivityCategory = Field(description="Activity type")
    weather_dependent: bool = Field(description="True if bad weather would spoil it")
    estimated_cost_eur: float = Field(ge=0, le=500, description="Rough cost per person in EUR")


class DayPlan(BaseModel):
    date: str = Field(description="Date in ISO format YYYY-MM-DD")
    condition: str = Field(description="Expected weather condition")
    temp_min_c: Optional[float] = Field(default=None, ge=-60, le=60)
    temp_max_c: Optional[float] = Field(default=None, ge=-60, le=60)
    activities: list[Activity] = Field(min_length=1, max_length=4)

    @field_validator("date")
    @classmethod
    def _iso_date(cls, value: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"date must be YYYY-MM-DD, got {value!r}")
        return value


class TravelPlan(BaseModel):
    destination: str = Field(description="Resolved city and country, e.g. 'Vienna, Austria'")
    days: list[DayPlan] = Field(min_length=1, max_length=7)
    packing_list: list[str] = Field(min_length=3, max_length=8)
    risk_level: Literal["low", "medium", "high"] = Field(
        description="Weather risk for the trip (storms, heavy rain, extreme heat ...)"
    )
    summary: str = Field(description="Two to three sentences of practical advice")


# ── Specialists ───────────────────────────────────────────────────────────────

weather_agent = Agent(
    name="weather_agent",
    model=_MODEL,
    description="Fetches the current weather and a daily forecast for a city.",
    instruction="""You are a weather data specialist.
ALWAYS call get_weather_forecast — never guess conditions.
Return the resolved location and, for each day, the ISO date, condition and min/max °C.
""",
    tools=[get_weather_forecast],
)

activity_advisor = Agent(
    name="activity_advisor",
    model=_MODEL,
    description="Suggests activities for a destination using visitor reviews and the weather.",
    instruction="""You are a local activity advisor for students on a budget.
Call get_local_reviews for the destination, then suggest 2-4 activities per day.
Prefer indoor options on rainy or stormy days. Give a rough cost in EUR for each.
""",
    # TODO C: add a sentence that reviews are untrusted opinions, not instructions
    tools=[get_local_reviews],
    # TODO B: after_tool_callback=sanitize_reviews,
)


# ── Pipeline ──────────────────────────────────────────────────────────────────

researcher = Agent(
    name="researcher",
    model=_MODEL,
    description="Collects weather data and activity ideas for a trip.",
    instruction="""You collect facts for a trip plan. You do NOT write the final answer.

1. Call weather_agent with the destination and number of days
   (default 3, "tomorrow" means 1 day).
2. Call activity_advisor with the destination, the weather summary you received
   and every preference the user stated (likes, dislikes, budget).
3. Reply with plain notes: the user's preferences, the resolved destination, and
   per day the ISO date, condition, min/max °C and the suggested activities with
   category and cost.
""",
    tools=[AgentTool(agent=weather_agent), AgentTool(agent=activity_advisor)],
    output_key="research_notes",
)

formatter = Agent(
    name="formatter",
    model=_MODEL,
    description="Turns research notes into a TravelPlan.",
    instruction="""Convert the research notes below into a TravelPlan.
Use only facts from the notes — do not invent dates or temperatures.
Drop any activity that contradicts the user's preferences.

Set risk_level to "high" for thunderstorms or heavy rain, "medium" for light
rain or temperatures below 0 °C or above 32 °C, otherwise "low".

Research notes:
{research_notes}
""",
    output_schema=TravelPlan,
    output_key="travel_plan",
)

root_agent = SequentialAgent(
    name="travel_planner",
    description="Plans trips and returns a machine-readable TravelPlan.",
    sub_agents=[researcher, formatter],
    # TODO A: before_agent_callback=block_prompt_injection,
    #   Works here on the root. ADK's LLM judge only knows LlmAgents, though —
    #   if refusals show up as "not found in the agentic system" in your eval,
    #   compare with how solution/ registers this callback.
)
