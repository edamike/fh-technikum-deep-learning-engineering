"""Agent with Session Persistence — Google ADK.

Lecture 5 · Section 2: Add Persistence · SOLUTION
─────────────────────────────────────────────────
Demonstrates:
- ToolContext: writing last_location to session state from within a tool
- DatabaseSessionService: persisting state in PostgreSQL across restarts
- InMemorySessionService: automatic fallback when DATABASE_URL is not set
- Runner: ADK execution engine that wires agent + session service together
- Multi-turn conversation loop via runner.run_async()

Run with PostgreSQL (recommended):
  docker compose up -d          # start Postgres (from this directory)
  python agent.py               # run the CLI

Run without PostgreSQL (in-memory fallback):
  python agent.py               # DATABASE_URL not set → uses InMemory
  # or via adk web:
  cd lecture5 && adk web 02_add_persistence/solution
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai.types import Content, Part
from .tools.weather_tool import get_weather_forecast


def _get_model():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="openai/Qwen/Qwen3.6-35B-A3B")
    return "gemini-3.8-flash"

_MODEL = _get_model()

APP_NAME = "weather_app"
USER_ID = "student_1"


root_agent = Agent(
    name="weather_agent",
    model=_MODEL,
    description="A weather agent that remembers your last searched location.",
    instruction="""You are a professional weather assistant with memory.

ALWAYS call get_weather_forecast for any location question — never guess.

If the user asks a follow-up without specifying a location (e.g. "what about tomorrow?",
"is it going to rain?"), use the last_location from session state as the location.

Format your answer with current conditions, a short forecast table, and one practical tip.
""",
    tools=[get_weather_forecast],
)


def _create_session_service():
    """Create a session service — PostgreSQL if DATABASE_URL is set, InMemory otherwise."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        from google.adk.sessions import DatabaseSessionService
        print(f"[persistence] Using PostgreSQL: {db_url.split('@')[-1]}")
        return DatabaseSessionService(db_url=db_url)
    else:
        from google.adk.sessions import InMemorySessionService
        print("[persistence] DATABASE_URL not set — using InMemorySessionService (state lost on restart)")
        print("[persistence] To use PostgreSQL: docker compose up -d, then set DATABASE_URL in .env")
        return InMemorySessionService()


session_service = _create_session_service()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


async def run_conversation():
    """Run an interactive multi-turn conversation with session persistence.

    The agent remembers which city was last searched within a session
    (stored in session state by the tool), so follow-up questions work.
    """
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    print("\nWeather Agent ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        message = Content(role="user", parts=[Part(text=user_input)])

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"Agent: {part.text}\n")
                        break


if __name__ == "__main__":
    asyncio.run(run_conversation())
