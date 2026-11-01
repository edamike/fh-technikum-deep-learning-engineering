# Section 1 — Constrained Decoding · Scaffold

Make the final answer of **your** Lecture 5 multi-agent system machine-readable.
The weather / activity specialists in `agent.py` are placeholders — replace
them with your own from Lecture 5 · Section 3.

## Your task (`agent.py`)

1. **Design a Pydantic schema** for your final answer. Use every constraint
   level from the lecture at least once:
   - `Literal["a", "b"]` — fixed set of values
   - `Field(ge=..., le=...)`, `min_length` — flat value constraints
   - a nested model or a `list[...]` of models — recursive structure
2. **researcher** — calls your specialists via `AgentTool(agent=...)` and
   writes plain notes to `output_key="research_notes"`.
3. **formatter** — no tools, `output_schema=YourSchema`, reads
   `{research_notes}` in its instruction.
4. Chain both in the `SequentialAgent`.

## Run

```bash
# from the repo root
.venv/bin/adk web lecture6/01_constrained_decoding
```

Select `scaffold`. Your structured answer appears in the **State** tab.

## Experiment

Put `output_schema` directly on the researcher (the agent that has tools).
Does it still call its tools? Compare the weather data in the answer with the
real forecast.

Compare with `solution/` after the lecture.
