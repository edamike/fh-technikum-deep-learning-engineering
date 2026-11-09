# Section 3 — Multi-Agent · Scaffold

Build a multi-agent system: one orchestrator + two specialist sub-agents.
Choose any domain — the weather/travel example is in `solution/` for reference.

## Quick start

From the repo root:

```bash
.venv/bin/adk web lecture5/03_multi_agent
```

Open **http://127.0.0.1:8000** and pick `scaffold` from the dropdown.

## Your task

Complete the three TODO groups in `agent.py`:

**TODO 1 — `sub_agent_a` (data-fetching specialist):**
- Give it a name and description
- Write an instruction that defines its specialty
- Add a tool (from Section 1, or a new one)

**TODO 2 — `sub_agent_b` (reasoning specialist, no tools):**
- Give it a name and description
- Write an instruction that defines what it analyses or produces
- Leave `tools=[]` — specialisation comes from the instruction alone

**TODO 3 — `root_agent` (orchestrator):**
- Give it a name
- Write an instruction that describes *when* to delegate to each sub-agent
  and how to combine their outputs for complex requests
- Set `sub_agents=[sub_agent_a, sub_agent_b]`

## Domain ideas

| Root agent | sub_agent_a (tool) | sub_agent_b (reasoning) |
|---|---|---|
| Travel Planner | weather fetcher | activity advisor |
| Research Lead | web/news searcher | summariser |
| Customer Support | FAQ lookup | escalation drafter |
| Code Helper | syntax checker | explainer |

## Run your scaffold

```bash
# from the lecture5/ directory
cd lecture5
adk web 03_multi_agent/scaffold
```

Open **http://localhost:8000**, select your root agent.
Use the **Events / Traces** tab to see delegation in action.

## Compare with the solution

```bash
adk web 03_multi_agent/solution
```
