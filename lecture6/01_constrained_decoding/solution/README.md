# Section 1 — Constrained Decoding · Solution

The Lecture 5 travel planner, now returning a machine-readable `TravelPlan`
(Pydantic) instead of free text.

```
travel_planner_structured (SequentialAgent)
  ├── researcher   tools: AgentTool(weather_agent), AgentTool(activity_advisor)
  │                → state["research_notes"]  (free text)
  └── formatter    output_schema=TravelPlan, no tools
                   → state["travel_plan"]     (validated JSON)
```

## Prerequisites

```bash
# from the repo root
pip install -r requirements.txt
cp .env.example .env     # Default: FH Lion (OPENAI_API_KEY). USE_LOCAL_LLM=false → Gemini.
```

## Run

```bash
# from the repo root
.venv/bin/adk web lecture6/01_constrained_decoding
```

Open **http://localhost:8000**, select `solution`, and try:

> "Plan a 2 day trip to Salzburg."
> "Weekend in Innsbruck, I hate museums."

Open the **State** tab: `travel_plan` holds the validated JSON object.

## What to look at

| Concept (lecture) | Where in `agent.py` |
|---|---|
| Fixed list of values — prefix trie | `Literal[...]` on `category`, `risk_level` |
| Flat constraints — finite state automaton | `ge` / `le` / `min_length` / `max_length` |
| Nested structure — context-free grammar | `TravelPlan → DayPlan → Activity` |
| Syntax ≠ semantics | `field_validator` on `DayPlan.date` runs *after* decoding |

## Why two agents instead of one?

Try it: move `output_schema=TravelPlan` onto the `researcher` and watch the
**Events** tab. When the decoder is forced to emit JSON from the first token,
the model can no longer emit a tool call — it returns valid-looking JSON with
**invented** weather data. That is the "reasoning suppression" challenge from
the slides. Gather first, format second.

## Why `AgentTool` instead of `sub_agents`?

With `sub_agents` the parent *transfers* the conversation and the sub-agent's
free-text reply becomes the final answer — the schema is never applied.
`AgentTool` calls the specialist like a function and returns its answer to the
caller, which keeps control.

> `SequentialAgent` prints a deprecation warning in ADK 2.11 (it is being
> replaced by the new `Workflow` graph API). It still works and is the simplest
> way to express "step 1, then step 2".
