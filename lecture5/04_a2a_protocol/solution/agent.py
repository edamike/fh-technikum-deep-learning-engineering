"""Travel Planner — Google ADK Multi-Agent System over A2A.

Lecture 5 · Section 4: A2A Protocol · SOLUTION
──────────────────────────────────────────────
Same travel planner as Section 3, but the two specialists live in separate
processes and the orchestrator talks to them over Google's open
Agent-to-Agent protocol (A2A, JSON-RPC over HTTP + SSE).

Pipeline:
  travel_planner  (this file, served by `adk web`)
    ├── RemoteA2aAgent → http://localhost:8001  (weather_server.py)
    └── RemoteA2aAgent → http://localhost:8002  (advisor_server.py)

Each remote server publishes an Agent Card at
`/.well-known/agent-card.json`; `RemoteA2aAgent` fetches it on first call
to discover the remote agent's name, description and capabilities.

Prerequisites — start the specialists first:
  Terminal 1:  python ../weather_server.py
  Terminal 2:  python ../advisor_server.py
  Terminal 3:  adk web lecture5/04_a2a_protocol
"""

import os

from google.adk.a2a.agent import RemoteA2aAgent
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"


_MODEL = _get_model()

WEATHER_CARD = os.getenv(
    "WEATHER_AGENT_CARD",
    "http://localhost:8001/.well-known/agent-card.json",
)
ADVISOR_CARD = os.getenv(
    "ADVISOR_AGENT_CARD",
    "http://localhost:8002/.well-known/agent-card.json",
)


# ── Remote specialists (A2A clients) ──────────────────────────────────────────
# Nothing is fetched here — the URL is stored. The agent card is resolved on
# first invocation, so `adk web` starts fine even if the servers are not yet up.

weather_agent = RemoteA2aAgent(
    name="weather_agent",
    agent_card=WEATHER_CARD,
    description="Remote weather specialist. Returns live weather and a daily forecast.",
)

activity_advisor = RemoteA2aAgent(
    name="activity_advisor",
    agent_card=ADVISOR_CARD,
    description="Remote activity advisor. Suggests activities for a destination and weather.",
)


# ── Root agent (identical orchestration to Section 3) ────────────────────────

root_agent = Agent(
    name="travel_planner_a2a",
    model=_MODEL,
    instruction="""You are a Travel Planner assistant for FH Technikum Wien students.

You have two tools that reach remote specialists over A2A:
- `weather_agent(request)` — fetches live weather and a daily forecast.
- `activity_advisor(request)` — suggests activities given a destination and weather.

For trip or destination questions you MUST call BOTH tools, in this order:
1. Call `weather_agent` with the destination and number of days.
2. Call `activity_advisor` with the destination AND the weather summary you just received.
3. Combine both responses into one concise travel briefing.

For weather-only questions: call `weather_agent` alone.
For activity-only questions: call `activity_advisor` alone.
Be friendly, concise, and practical.
""",
    # AgentTool wraps each remote so the orchestrator calls them like functions
    # and keeps control — with sub_agents=[...] the first transfer_to_agent would
    # hand the whole turn to weather_agent and advisor would never be called.
    tools=[AgentTool(agent=weather_agent), AgentTool(agent=activity_advisor)],
)
