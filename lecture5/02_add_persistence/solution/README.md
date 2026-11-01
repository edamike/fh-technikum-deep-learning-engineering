# Section 2 — Add Persistence · Solution

A weather agent with session memory backed by **PostgreSQL**.
The agent stores the last searched city in `session.state` via `ToolContext`,
so follow-up questions like *"what about tomorrow?"* work without repeating the location.

Falls back to `InMemorySessionService` automatically if `DATABASE_URL` is not set.

---

## Option A — With PostgreSQL (recommended)

### 1. Start the database

```bash
# from this directory (lecture5/02_add_persistence/)
docker compose up -d
```

Starts a PostgreSQL container on `localhost:5432`.
ADK creates the session tables automatically on first run.

Stop it later with:
```bash
docker compose down          # stops but keeps data
docker compose down -v       # stops and deletes data
```

### 2. Configure the connection

In your `.env` file (repo root), set:
```
DATABASE_URL=postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions
```

This matches the defaults in `docker-compose.yml`. Change only if you customise them.

### 3. Run

**CLI (best for demonstrating persistence):**
```bash
cd lecture5/02_add_persistence/solution
python agent.py
```

Try this conversation to see persistence in action:
```
You: What's the weather in Vienna?
Agent: [returns Vienna weather and stores "Vienna" in session state]

You: What about tomorrow?
Agent: [uses "Vienna" from session state — no need to repeat it]
```

**adk web (with PostgreSQL):**

`adk web` does not use the `session_service` defined in `agent.py` — it creates its own.
Pass the Postgres connection via `--session_service_uri`:

```bash
# from the repo root
.venv/bin/adk web lecture5/02_add_persistence \
    --session_service_uri="postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions"
```

Open **http://localhost:8000** and select `solution` in the agent dropdown.
Check the **State** tab to see `last_location` being stored. Sessions survive
restarting `adk web` — they are listed under **Sessions** and stored in Postgres.

---

## Option B — Without PostgreSQL (in-memory fallback)

Leave `DATABASE_URL` unset in `.env`. The agent logs a notice and uses
`InMemorySessionService` — state works within a session but is lost on restart.

```bash
# CLI
cd lecture5/02_add_persistence/solution
python agent.py

# or adk web without --session_service_uri (in-memory sessions)
.venv/bin/adk web lecture5/02_add_persistence
```

---

## Prerequisites

```bash
pip install -r requirements.txt        # includes asyncpg + sqlalchemy
cp .env.example .env                   # default: FH Lion; USE_LOCAL_LLM=false → Gemini
```

---

## What to look at

| File | What it shows |
|------|---------------|
| `tools/weather_tool.py` | `ToolContext` parameter + `tool_context.state["last_location"] = ...` |
| `agent.py` | `_create_session_service()` switches between Postgres and InMemory |
| `agent.py` | `Runner` + `run_conversation()` multi-turn loop |
| `docker-compose.yml` | Minimal Postgres setup for local development |
