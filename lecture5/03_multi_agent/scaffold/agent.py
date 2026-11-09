"""Multi-Agent System — Google ADK.

Lecture 5 · Section 3: Multi-Agent with sub_agents · SCAFFOLD
─────────────────────────────────────────────────────────────
Goal: Build a multi-agent system where a root (orchestrator) agent
delegates to two specialised sub-agents.

You choose the domain. The weather/travel example is provided in solution/.
Some other ideas:

  Domain: Research Assistant
    sub_agent_a: web_searcher  (calls a search/news API)
    sub_agent_b: summariser    (pure LLM, no tools — summarises content)
    root_agent:  research_lead (orchestrates: search first, then summarise)

  Domain: Customer Support
    sub_agent_a: faq_agent     (tool: FAQ database lookup)
    sub_agent_b: escalation_agent (no tools — drafts human-escalation emails)
    root_agent:  support_router   (routes: simple → faq, complex → escalation)

  Domain: Travel Planner (see solution/ for reference)
    sub_agent_a: weather_agent   (tool: weather API)
    sub_agent_b: activity_advisor (no tools — recommends activities)
    root_agent:  travel_planner  (fetches weather, then recommends activities)

Architecture:
  root_agent
    ├── sub_agent_a   ← has tools (fetches real data)
    └── sub_agent_b   ← no tools (reasoning only, specialised instruction)

Key concept:
  • sub_agents=[...]  The root agent delegates tasks to sub-agents.
                      The LLM decides which sub-agent to invoke based on their
                      descriptions and the user's request.
  • Each sub-agent maintains its own context, tools, and instruction.
  • The root agent NEVER calls tools directly — it only orchestrates.

TODOs are marked below. When done, run:  adk web 03_multi_agent/scaffold
"""

import os
from google.adk.agents import Agent

# Import your tool — update this if you use a different tool file/function
from .tools.weather_tool import get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()


# ── Sub-Agent A: Data Fetcher (with tool) ─────────────────────────────────────
# This sub-agent has a tool and fetches real data.
# In the weather example this is the weather_agent.
# Replace with your own specialist (search agent, database agent, etc.).
#
# TODO 1: Define sub_agent_a
#   - name: a descriptive snake_case name
#   - instruction: tell it what it specialises in and WHEN to call its tool
#   - tools: one or more tools
#
# Teaching point: the description field matters here — the root agent reads it
# to decide when to delegate to this sub-agent.

sub_agent_a = Agent(
    name="TODO_data_fetcher",        # TODO 1a — give it a descriptive name
    model=_MODEL,
    description="TODO — describe what this agent specialises in (one sentence).",
    instruction="""TODO 1b — write the specialist instruction.

  - What domain does this agent cover?
  - When must it call its tool?
  - What format should it return?
""",
    tools=[],                        # TODO 1c — add your tool(s)
)


# ── Sub-Agent B: Reasoning Specialist (no tools) ──────────────────────────────
# This sub-agent has NO tools — it uses only LLM knowledge.
# Specialisation comes entirely from the instruction.
# In the weather example this is the activity_advisor.
#
# TODO 2: Define sub_agent_b
#   - name: a descriptive snake_case name
#   - instruction: tell it its specialty and expected output format
#   - No tools needed (that's the point — pure reasoning sub-agent)

sub_agent_b = Agent(
    name="TODO_reasoning_specialist",  # TODO 2a
    model=_MODEL,
    description="TODO — describe what this agent specialises in (one sentence).",
    instruction="""TODO 2b — write the specialist instruction.

  - What kind of analysis or output does this agent produce?
  - What input does it expect (from the root agent or from the user)?
  - What format should it return?
""",
    # No tools — intentional
)


# ── Root Agent: Orchestrator ───────────────────────────────────────────────────
# The root agent decides how to delegate to sub_agent_a and sub_agent_b.
# It never calls tools directly — its job is coordination.
#
# TODO 3: Define root_agent
#   - name: a descriptive orchestrator name
#   - instruction: describe the delegation strategy:
#       • when to call sub_agent_a (data fetching questions)
#       • when to call sub_agent_b (analysis/reasoning questions)
#       • how to combine both for complex requests
#   - sub_agents: [sub_agent_a, sub_agent_b]

root_agent = Agent(
    name="TODO_orchestrator",       # TODO 3a
    model=_MODEL,
    description="An orchestrator agent that delegates to specialist sub-agents.",
    instruction="""TODO 3b — write the orchestration instruction.

  Describe your delegation strategy:
  - For <type A> questions → delegate to sub_agent_a
  - For <type B> questions → delegate to sub_agent_b
  - For complex requests   → use both sub-agents and synthesise the results
""",
    sub_agents=[],                  # TODO 3c — add [sub_agent_a, sub_agent_b]
)
