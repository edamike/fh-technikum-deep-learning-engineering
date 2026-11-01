"""Multi-Agent System with Constrained Decoding — Google ADK.

Lecture 6 · Section 1: Constrained Decoding · SCAFFOLD
──────────────────────────────────────────────────────
Goal: Make the final answer of your multi-agent system machine-readable by
forcing it into a Pydantic schema (`output_schema` → constrained decoding).

Start from YOUR multi-agent system from Lecture 5 · Section 3. The weather /
activity specialists below are only placeholders — replace them with yours.

Target pipeline:

    researcher  ──(free text, calls the specialists)──▶  state["research_notes"]
    formatter   ──(output_schema=YourSchema, no tools)──▶ state["final_output"]

Why two steps? If the decoder is forced to emit JSON from the first token,
the model can never emit a tool call. Try it: put output_schema directly on the
researcher and watch the trace in `adk web` — does it still call its tools?

TODOs are marked below. Run with:  adk web lecture6/01_constrained_decoding
"""

import os
from typing import Literal, Optional

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .tools.weather_tool import get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()


# ── TODO 1: Design your output schema ─────────────────────────────────────────
# Use all three constraint levels from the lecture at least once:
#
#   Literal["a", "b", "c"]             fixed set of values      (prefix trie)
#   Field(ge=0, le=100), min_length=1  flat value constraints   (finite state automaton)
#   nested BaseModel / list[...]       recursive structure      (context-free grammar)
#
# Give every field a `description=` — the model sees it, just like a tool docstring.
#
# Example for a travel planner (replace with your own domain):
#   class Activity(BaseModel):
#       name: str
#       category: Literal["outdoor", "indoor", "food"]
#       estimated_cost_eur: float = Field(ge=0, le=500)

class Item(BaseModel):
    """TODO: rename and add the fields of one nested element."""
    name: str = Field(description="TODO")


class FinalOutput(BaseModel):
    """TODO: rename and design the top-level structure of your answer."""
    title: str = Field(description="TODO")
    items: list[Item] = Field(description="TODO")


# ── Specialists (paste yours from Lecture 5 · Section 3) ────────────────────────

specialist_a = Agent(
    name="weather_agent",
    model=_MODEL,
    description="Fetches the current weather and a daily forecast for a city.",
    instruction="You are a weather specialist. ALWAYS call get_weather_forecast — never guess.",
    tools=[get_weather_forecast],
)

specialist_b = Agent(
    name="activity_advisor",
    model=_MODEL,
    description="Suggests activities for a destination given a weather summary.",
    instruction="Suggest 2-4 budget-friendly activities per day for the given destination and weather.",
)


# ── TODO 2: researcher ────────────────────────────────────────────────────────
#   - wrap the specialists with AgentTool(agent=...) and pass them as tools
#     (AgentTool keeps control in the researcher; sub_agents would transfer it away)
#   - instruction: which specialist to call in which order, and to reply with
#     plain notes containing every fact the schema needs
#   - output_key="research_notes"  → stores the reply in session state

researcher = Agent(
    name="researcher",
    model=_MODEL,
    instruction="TODO",
    tools=[],               # TODO: [AgentTool(agent=specialist_a), AgentTool(agent=specialist_b)]
    # TODO: output_key=...
)


# ── TODO 3: formatter ─────────────────────────────────────────────────────────
#   - NO tools
#   - output_schema=FinalOutput   → constrained decoding happens here
#   - output_key="final_output"
#   - instruction: convert the notes into the schema; reference them with
#     {research_notes} — ADK replaces it with the value from session state

formatter = Agent(
    name="formatter",
    model=_MODEL,
    instruction="TODO — include {research_notes} somewhere in this text",
    # TODO: output_schema=..., output_key=...
)


# ── TODO 4: chain both steps ──────────────────────────────────────────────────

root_agent = SequentialAgent(
    name="structured_planner",
    sub_agents=[],          # TODO: [researcher, formatter]
)
