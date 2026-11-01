# Section 4 — A2A Protocol · Solution

The Section 3 travel planner, re-wired so the two specialists run as
**separate processes** that the orchestrator reaches over Google's open
**[Agent-to-Agent (A2A)](https://a2aproject.github.io/A2A/)** protocol
(JSON-RPC + SSE over HTTP). The weather specialist then calls its Open-Meteo
tool over a second standard — the **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)**
— through an auto-spawned stdio subprocess:

```
┌─ adk web (localhost:8000) ────────────────┐
│                                            │
│  travel_planner_a2a                        │
│    ├─ RemoteA2aAgent ──A2A──► :8001 (weather_server.py)
│    │                             │
│    │                             └─MCP(stdio)─► mcp_weather_server.py ──HTTP──► Open-Meteo
│    │
│    └─ RemoteA2aAgent ──A2A──► :8002 (advisor_server.py)   (reasoning only — no tools)
└────────────────────────────────────────────┘
```

Each A2A specialist publishes an **Agent Card** at
`/.well-known/agent-card.json` — the orchestrator fetches it on first call
to learn the remote's name, description, skills and streaming capability.
The MCP subprocess is spawned lazily by the weather specialist on first tool
call; it is **not** started manually.

> **Two protocols, two jobs.** A2A moves *tasks between agents*. MCP moves
> *tool calls between an agent and an external capability provider*. They
> stack naturally: here the orchestrator reaches the weather specialist via
> A2A, and the weather specialist reaches its weather tool via MCP.

## Prerequisites

The `a2a` extra is pulled in by the shared `requirements.txt` (`google-adk[a2a]`),
so no separate install is needed if you've installed the course dependencies.

## Run

Open **three terminals** (or use a process manager — see "No multiple terminals?" below).

**Terminal 1 — weather specialist**
```bash
cd lecture5/04_a2a_protocol
python weather_server.py
# listens on http://localhost:8001
```

**Terminal 2 — activity advisor**
```bash
cd lecture5/04_a2a_protocol
python advisor_server.py
# listens on http://localhost:8002
```

**Terminal 3 — orchestrator (ADK web UI)**
```bash
cd lecture5
adk web 04_a2a_protocol
```

Open **http://localhost:8000**, select `solution`, and try:

> "Plan a day trip to Salzburg this weekend."
> "What can I do in Graz? Is the weather good?"

The **Events / Traces** tab shows the root agent dispatching A2A tasks to
each remote. The specialist processes log every incoming request to their
terminal — proof that the work is happening across the network.

## What to look at

| File | What it shows |
|------|---------------|
| `specialists.py` | ADK LlmAgents; `weather_agent` uses an `McpToolset` instead of the Python function directly |
| `mcp_weather_server.py` | FastMCP server — one `@mcp.tool()` wrapping Open-Meteo, served over stdio |
| `weather_server.py` / `advisor_server.py` | `to_a2a(agent)` → Starlette app, served with uvicorn |
| `solution/agent.py` | Root agent uses `RemoteA2aAgent` instead of in-process sub-agents |

Visit `http://localhost:8001/.well-known/agent-card.json` in your browser —
the JSON there is what the A2A client fetches to discover the agent. The
`skills` array shows `weather_agent-get_weather_forecast` — the tool name
that bubbled up from the MCP subprocess into the public Agent Card.

## In-process vs. A2A — what changed?

| | Section 3 (in-process) | Section 4 (A2A) |
|---|---|---|
| Specialist location | same Python process | separate uvicorn process |
| Wiring | `sub_agents=[LlmAgent, LlmAgent]` | `sub_agents=[RemoteA2aAgent, RemoteA2aAgent]` |
| Discovery | Python import | Agent Card at `/.well-known/agent-card.json` |
| Transport | in-memory function calls | JSON-RPC over HTTP + SSE |
| Failure modes | exceptions bubble up | add: timeouts, connection refused, cold starts |
| Deployment | one artifact | one artifact per agent (independent scaling, versioning) |

The orchestrator's instruction and reasoning are **unchanged** — the only
difference is where the sub-agents live and how the bytes travel.

## Overriding endpoints

Set env vars before launching `adk web` (useful in docker-compose or
Kubernetes where host/port differ):

```bash
WEATHER_AGENT_CARD=http://weather:8001/.well-known/agent-card.json \
ADVISOR_AGENT_CARD=http://advisor:8002/.well-known/agent-card.json \
adk web 04_a2a_protocol
```

## No multiple terminals?

Run both servers in the background from one shell:

```bash
cd lecture5/04_a2a_protocol
python weather_server.py &
python advisor_server.py &
cd ..
adk web 04_a2a_protocol
# when done:  kill %1 %2
```

## Troubleshooting

**`httpx.ConnectError` on first message in `adk web`** — the specialist
servers are not up yet. Start them in another terminal and retry.

**Experimental warnings** — ADK's A2A integration is still marked
experimental. The underlying A2A protocol and SDK are stable; the ADK
glue code API may still change.
