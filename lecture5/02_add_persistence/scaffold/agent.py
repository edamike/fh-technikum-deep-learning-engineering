"""Agent with Session Persistence — Google ADK.

Lecture 5 · Section 2: Add Persistence · SCAFFOLD
─────────────────────────────────────────────────
Goal: Extend your agent from Section 1 so it "remembers" context across turns
within a session, backed by a real PostgreSQL database.

Motivation:
  Without persistence, each turn is stateless — the agent forgets everything.
  With persistence, follow-up questions work naturally:
    User: "What's the weather in Vienna?"    → agent fetches & stores "Vienna"
    User: "What about tomorrow?"             → agent recalls "Vienna" from state

Two persistence backends (you choose via DATABASE_URL in .env):
  • PostgreSQL  (recommended) — start with:  docker compose up -d
  • InMemory    (fallback)    — no setup needed, state lost on restart

TODOs are split between this file and tools/weather_tool.py.
─────────────────────────────────────────────────
Replace the weather tool / agent with your own domain if you prefer.
"""

import asyncio
import os
from google.adk.agents import Agent

# Replace this import if you use a different tool
from .tools.weather_tool import get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()

APP_NAME = "my_agent_app"   # change to match your agent's domain
USER_ID = "student_1"


# ── Agent definition ───────────────────────────────────────────────────────────
# Reuse your agent from Section 1 — or define a new one here.
# Add a reference to session state in the instruction so the agent uses it.

root_agent = Agent(
    name="my_agent",
    model=_MODEL,
    description="An agent with session persistence.",
    instruction="""You are a helpful assistant with memory.

Always use your tool to fetch information — never rely on internal knowledge alone.

If the user asks a follow-up question without specifying a key parameter
(e.g. asks "what about tomorrow?" without a city), check session state for
the last value the user provided and reuse it.

Be concise and friendly.
""",
    tools=[get_weather_forecast],   # replace with your own tool(s)
)


# ── TODO A: Create the session service ────────────────────────────────────────
# Choose PostgreSQL if DATABASE_URL is set, otherwise fall back to InMemory.
#
# PostgreSQL (requires docker compose up -d from this directory):
#   from google.adk.sessions import DatabaseSessionService
#   db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions")
#   session_service = DatabaseSessionService(db_url=db_url)
#
# InMemory (no setup, state lost on restart):
#   from google.adk.sessions import InMemorySessionService
#   session_service = InMemorySessionService()
#
# Tip: use os.getenv("DATABASE_URL") to switch automatically.

# TODO A: uncomment and complete the session service setup
# session_service = ...


# ── TODO B: Create the Runner ─────────────────────────────────────────────────
# The Runner wires together your agent, the app name, and the session service.
#
#   from google.adk.runners import Runner
#   runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

# TODO B: uncomment and create the runner
# runner = ...


# ── TODO C: Implement run_conversation() ──────────────────────────────────────
# 1. Create a session:  session = await session_service.create_session(...)
# 2. Loop: read user input → wrap in Content → run via runner.run_async(...)
# 3. Print the final response (check event.is_final_response())
# 4. Exit on "quit" or "exit"
#
#   from google.genai.types import Content, Part
#   message = Content(role="user", parts=[Part(text=user_input)])
#   async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=message):
#       if event.is_final_response() and event.content:
#           print(event.content.parts[0].text)

async def run_conversation():
    """Multi-turn conversation loop with session persistence."""
    # TODO C: implement me
    print("Persistence not yet set up — complete TODOs A, B, and C.")


if __name__ == "__main__":
    asyncio.run(run_conversation())
