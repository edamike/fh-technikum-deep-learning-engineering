# Section 2 — Add Persistence · Scaffold

Extend your agent from Section 1 with session memory.

## Your task

Complete the three TODO groups:

**`tools/weather_tool.py` (or your own tool):**
- Import `ToolContext`
- Add `tool_context: ToolContext = None` as the last parameter
- Write a meaningful value to `tool_context.state[...]` after a successful call

**`agent.py TODO A` — session service:**
```python
# With PostgreSQL (see docker-compose.yml):
from google.adk.sessions import DatabaseSessionService
session_service = DatabaseSessionService(db_url=os.getenv("DATABASE_URL"))

# Without PostgreSQL (in-memory fallback):
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()
```

**`agent.py TODO B` — runner:**
```python
from google.adk.runners import Runner
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
```

**`agent.py TODO C` — conversation loop:**
```python
from google.genai.types import Content, Part
session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
message = Content(role="user", parts=[Part(text=user_input)])
async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=message):
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
```

## Optional: start PostgreSQL

```bash
# from this directory (lecture5/02_add_persistence/)
docker compose up -d
```

Then set in `.env`:
```
DATABASE_URL=postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions
```

Skip this if you use `InMemorySessionService`.

## Run your scaffold

```bash
# CLI mode
cd lecture5/02_add_persistence/scaffold
python agent.py

# or via adk web
cd lecture5
adk web 02_add_persistence/scaffold
```
