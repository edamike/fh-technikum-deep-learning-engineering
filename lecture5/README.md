# Lecture 5 — Agent Architecture

**Deep Learning Engineering · FH Technikum Wien**

This lecture introduces Google ADK hands-on.

| Section | Concept |
|---------|---------|
| `01_single_agent` | Agent + tool (ReAct / Tool Calling) |
| `02_add_persistence` | Session state (PostgreSQL) + vector-RAG (Chroma + local sentence-transformers embeddings) over a local Markdown corpus |
| `03_multi_agent` | Orchestrator + specialist sub-agents (in-process) |
| `04_a2a_protocol` | Same orchestration, specialists running as separate A2A services |

Sections 1–3 ship a **`scaffold/`** (starter code with `# TODO` markers for the lecture)
and a **`solution/`** (complete reference implementation). Section 4 ships only a
`solution/`: it builds on the Section 3 solution and is designed as a demo of
Google's open Agent-to-Agent protocol, not an exercise.

> **Use your own domain!** The scaffold files are intentionally domain-agnostic.
> The weather example is only one possibility — replace the tool and agent instructions
> with any domain you find interesting (news, stocks, Wikipedia, movies, recipes, etc.).

---

## Setup

```bash
# from the repo root
pip install -r requirements.txt
cp .env.example .env        # fill in OPENAI_API_KEY (FH Lion)
```

The default model is **FH Lion** (Qwen3.6-35B-A3B). To use Google Gemini
instead, set in `.env`:
```
USE_LOCAL_LLM=false
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Section 1 — Single Agent

Build an agent that answers questions by calling an external tool.
The weather example fetches live data from the Open-Meteo API — but you can use any API or function.

**Concepts:** Agent definition, tool registration, tool docstring as LLM contract, ReAct loop

```bash
cd lecture5
adk web 01_single_agent/solution
```

**Scaffold TODOs (`scaffold/`):**
1. Implement your tool in `tools/weather_tool.py` (or replace with your own file)
2. Fill in `agent.py`: name, instruction, and `tools=[your_tool]`

**Ideas for your own tool:** currency converter, Wikipedia summary, time zone lookup,
movie info (OMDb), joke/quote API, simple calculator.

---

## Section 2 — Add Persistence (+ local RAG)

Extend your agent with two complementary kinds of memory:
- **Short-term session state** backed by **PostgreSQL** — the weather and
  notes tools both write to `session.state` via `ToolContext`, so follow-up
  questions like *"what about tomorrow?"* or *"any cheap places to eat there?"*
  work without repeating the city.
- **Long-term corpus memory** — a vector-RAG tool (`retrieve_city_notes`)
  backed by Chroma + local sentence-transformers embeddings
  (`all-MiniLM-L6-v2`, ~80 MB cached on first use) over a handful of
  Markdown files in `02_add_persistence/city_notes/`, for questions the
  weather tool can't answer (cheap eats, transit, student discounts,
  rainy-day options, nightlife, day trips).

**Concepts:** `ToolContext.state`, `DatabaseSessionService`, `InMemorySessionService`,
`Runner`, multi-turn conversation loop, retrieval-augmented generation (RAG).

### Start the database

```bash
cd lecture5/02_add_persistence
docker compose up -d          # starts PostgreSQL on localhost:5432
```

Add to `.env` (already in `.env.example`):
```
DATABASE_URL=postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions
```

### Run

```bash
# interactive CLI (shows persistence clearly across turns)
cd lecture5/02_add_persistence/solution
python agent.py

# or via adk web
cd lecture5
adk web 02_add_persistence/solution
```

> **No Docker?** Leave `DATABASE_URL` unset — the solution falls back to
> `InMemorySessionService` automatically (state is lost on restart, but the
> conversation logic still works for the lecture demo).

**Scaffold TODOs:**
1. `tools/weather_tool.py`: import `ToolContext`, add as parameter, write `last_X` to state
2. `agent.py TODO A`: create the session service (Postgres or InMemory)
3. `agent.py TODO B`: create the `Runner`
4. `agent.py TODO C`: implement the `run_conversation()` loop

---

## Section 3 — Multi-Agent

Build a multi-agent system: one orchestrator root agent + two specialist sub-agents.
One sub-agent has a tool (fetches data); the other is reasoning-only (no tools).

**Concepts:** `sub_agents=[...]`, orchestrator pattern, specialisation via instruction,
tool-calling vs. reasoning-only sub-agents, separation of concerns

```bash
cd lecture5
adk web 03_multi_agent/solution
```

**Scaffold TODOs:**
1. Define `sub_agent_a` with a tool (your data-fetching specialist)
2. Define `sub_agent_b` with no tools (your reasoning/analysis specialist)
3. Define `root_agent` with `sub_agents=[sub_agent_a, sub_agent_b]` and an orchestration instruction

**Example architectures to try:**
- Travel planner: weather fetcher + activity advisor (see `solution/`)
- Research assistant: web/news searcher + summariser
- Customer support: FAQ lookup + escalation drafter
- Code helper: syntax checker + explainer

---

## Section 4 — A2A Protocol (demo)

The same travel planner, now distributed: each specialist runs as its own
A2A service, and the orchestrator reaches them over Google's open
Agent-to-Agent protocol (JSON-RPC + SSE over HTTP). Students see what
"multi-agent" looks like once it crosses process boundaries — Agent Cards,
network transport, independent deployment.

**Concepts:** `to_a2a()`, `RemoteA2aAgent`, Agent Cards at
`/.well-known/agent-card.json`, JSON-RPC task delegation.

```bash
# In three terminals:
cd lecture5/04_a2a_protocol && python weather_server.py    # :8001
cd lecture5/04_a2a_protocol && python advisor_server.py    # :8002
cd lecture5 && adk web 04_a2a_protocol                     # :8000
```

See `04_a2a_protocol/README.md` for the full walkthrough. Marked **experimental**
by ADK — the A2A protocol itself is stable; the ADK glue API may still change.

---

## Running any agent

```bash
cd lecture5
adk web <section>/<scaffold_or_solution>
# examples:
adk web 01_single_agent/solution
adk web 02_add_persistence/scaffold
adk web 03_multi_agent/solution
```

Open http://localhost:8000 in your browser.
