# Section 3 — Multi-Agent · Solution

A Travel Planner that orchestrates two specialist sub-agents:

- **`weather_agent`** — fetches live weather via the Open-Meteo API (tool-calling sub-agent)
- **`activity_advisor`** — recommends activities using LLM knowledge only (no tools)
- **`travel_planner`** — root agent that delegates to both and synthesises the result

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
adk web 03_multi_agent/solution
```

Open **http://localhost:8000** — select `travel_planner` and try:

> "Plan a day trip to Salzburg this weekend."
> "What can I do in Graz? Is the weather good?"
> "Suggest outdoor activities for Vienna tomorrow."

## What to look at

| File | What it shows |
|------|---------------|
| `agent.py` | Three agents: two sub-agents + one root orchestrator |
| `agent.py` | `sub_agents=[weather_agent, activity_advisor]` wires the system |
| `tools/weather_tool.py` | The same tool from Section 1, now inside a sub-agent |

In the **Events / Traces** tab you can see the root agent delegating to each
sub-agent in turn and then synthesising the final answer.

## Key concepts

**Tool-calling vs. reasoning-only sub-agents:**

| | `weather_agent` | `activity_advisor` |
|---|---|---|
| Has tools | yes — `get_weather_forecast` | no |
| Specialisation | fetching real-time data | reasoning from LLM knowledge |
| Instruction | "always call the tool" | "given a location + weather, suggest activities" |

**Why split into sub-agents?**
Each agent has a focused context window and instruction — the root agent never
accumulates all tool traces and reasoning in one growing prompt.
