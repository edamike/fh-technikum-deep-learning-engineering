"""Single Agent — Google ADK.

Lecture 5 · Section 1: Single Agent · SCAFFOLD
─────────────────────────────────────────────
Goal: Build an agent that answers questions by calling an external tool.
      The tool is what makes the agent "grounded" — it fetches real data
      instead of relying on potentially stale LLM knowledge.

You are free to use ANY domain for your agent. The weather example is provided
as a reference in the solution/ directory. Some other ideas:

  - A currency conversion agent (tool: exchange rate API)
  - A Wikipedia summary agent (tool: Wikipedia REST API)
  - A time zone agent (tool: worldtimeapi.org)
  - A movie info agent (tool: OMDb / TMDB API)
  - A simple calculator agent (tool: pure Python, no external API)

Steps:
  1. Pick your domain and define (or replace) the tool in tools/weather_tool.py
  2. Fill in the TODOs in this file to wire the tool to an agent
  3. Run:  adk web 01_single_agent/scaffold   from the lecture5/ directory

When it works, compare your solution with 01_single_agent/solution/.
"""

import os
from google.adk.agents import Agent

# Import your tool — rename or replace this import if you use a different tool file
from .tools.weather_tool import get_weather_forecast


def _get_model():
    """Returns the configured model (FH Lion by default, Gemini if USE_LOCAL_LLM=false)."""
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()


# ── Your Agent ────────────────────────────────────────────────────────────────
# TODO 1: Choose a name for your agent (descriptive, snake_case).
#
# TODO 2: Write an instruction that tells the agent:
#   - What it is / what domain it covers
#   - WHEN it must call the tool (always? only for certain questions?)
#   - What format to use for its answer
#
#   Tip: a clear, specific instruction leads to much better agent behaviour.
#   The instruction IS the agent's "brain" — invest time in it.
#
# TODO 3: Add your tool to the tools list.
#   The tool's docstring is what the LLM reads to decide when to call it —
#   make sure it clearly describes what the tool does and what it returns.

root_agent = Agent(
    name="TODO_give_me_a_name",              # TODO 1
    model=_MODEL,
    description="A single agent that answers questions using a tool.",
    instruction="""TODO 2: Write your instruction here.

Example structure:
  You are a <domain> assistant.
  Always use <tool_name> to fetch <what> before answering.
  Format your answer as: ...
""",
    tools=[],                                # TODO 3: add your tool, e.g. [get_weather_forecast]
)
