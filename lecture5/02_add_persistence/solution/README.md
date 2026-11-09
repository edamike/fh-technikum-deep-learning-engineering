# Section 2 — Add Persistence · Solution

A travel-companion agent with **two complementary kinds of memory**:

- **Short-term session state** (`ToolContext` → PostgreSQL / InMemory) — both
  tools write to session state (`last_location`, `last_retrieved_notes`), so
  follow-ups like *"what about tomorrow?"* or *"any cheap places to eat there?"*
  work without repeating the city.
- **Long-term corpus memory** (Chroma vector store + local
  sentence-transformers embeddings, over `../city_notes/*.md`) — the
  `retrieve_city_notes` tool answers questions the weather tool can't: cheap
  eats, transit, student discounts, rainy-day options, nightlife, day trips.
  No embedding API key needed; the model (`all-MiniLM-L6-v2`, ~80 MB) is
  downloaded once from HuggingFace and cached under `~/.cache/huggingface/`.

Falls back to `InMemorySessionService` automatically if `DATABASE_URL` is not set.

---

## Quick start

Start Postgres in one terminal (or skip — `adk web` will error loudly if it
can't reach the DB):

```bash
docker compose -f lecture5/02_add_persistence/docker-compose.yml up -d
```

Then from the repo root:

```bash
.venv/bin/adk web lecture5/02_add_persistence \
    --session_service_uri="postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions"
```

Open **http://127.0.0.1:8000**, pick `solution`, and ask *"Plan a rainy day in Graz."*

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

Try this conversation to see both kinds of memory in action:
```
You: Plan a rainy day in Graz — what can I do indoors?
Agent: [calls retrieve_city_notes(Graz, "rainy day indoor") AND get_weather_forecast(Graz)]
       → returns forecast + Landeszeughaus / Sackstraße galleries (from graz.md)
       → stores "Graz" in last_location and "last_retrieved_notes" in session state

You: Any cheap places to eat there?
Agent: [no city in message → uses last_location="Graz" from state]
       [calls retrieve_city_notes(Graz, "cheap eats")]
       → Uni-Mensa + Bauernmarkt, cites (graz.md)
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
pip install -r requirements.txt        # includes asyncpg + sqlalchemy + chromadb + sentence-transformers
cp .env.example .env                   # default: FH Lion for chat; no extra key needed for the RAG (local embedder)
```

---

## What to look at

| File | What it shows |
|------|---------------|
| `tools/weather_tool.py` | `ToolContext` parameter + `tool_context.state["last_location"] = ...` |
| `tools/notes_tool.py` | Chroma collection of `../city_notes/*.md` chunks, embedded locally via `sentence-transformers/all-MiniLM-L6-v2`; writes `last_retrieved_notes` to state |
| `../city_notes/*.md` | The local knowledge base — a handful of paragraph-sized chunks per city |
| `agent.py` | `_create_session_service()` switches between Postgres and InMemory |
| `agent.py` | `Runner` + `run_conversation()` multi-turn loop |
| `docker-compose.yml` | Minimal Postgres setup for local development |

---

## Two kinds of memory, side by side

| | Session state | Chroma vector store |
|---|---|---|
| Lifetime | One session | Rebuilt every process start |
| Scope | Per user | Shared read-only knowledge |
| Written by | Tools (via `ToolContext.state`) | Author of `../city_notes/*.md` |
| Backing store | Postgres / InMemory | In-memory Chroma collection |
| Access pattern | Key lookup | Semantic search (cosine over local 384-dim embeddings) |

Swapping the embedding model is a one-line change in `_embedder()` (any
model ID on the HuggingFace hub works); swapping Chroma for a persistent
store (pgvector, Vertex AI RAG, Qdrant) is a drop-in change in
`_collection()` — the retrieval interface the agent sees is the same.
