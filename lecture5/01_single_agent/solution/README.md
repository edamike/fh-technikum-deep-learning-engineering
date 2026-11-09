# Section 1 — Single Agent · Solution

A weather agent that calls the Open-Meteo API via a registered tool.

## Quick start

From the repo root:

```bash
.venv/bin/adk web lecture5/01_single_agent
```

Open **http://127.0.0.1:8000**, pick `solution`, ask *"What's the weather in Vienna this week?"*.

## Prerequisites

```bash
# from the repo root
pip install -r requirements.txt
cp .env.example .env
# Default: FH Lion (set OPENAI_API_KEY). Set USE_LOCAL_LLM=false + GEMINI_API_KEY to switch to Gemini.
```

## Run

```bash
# from the lecture5/ directory
cd lecture5
adk web 01_single_agent/solution
```

Open **http://localhost:8000** — select `weather_agent` and ask e.g.:

> "What's the weather in Vienna this week?"
> "Will it rain in Graz tomorrow?"

## What to look at

| File | What it shows |
|------|---------------|
| `tools/weather_tool.py` | A plain Python function registered as a tool |
| `agent.py` | `Agent(tools=[...])` wires the tool to the LLM |

The **Events / Traces** tab in the ADK web UI shows the full ReAct loop:
Thought → Tool call → Observation → Final answer.
