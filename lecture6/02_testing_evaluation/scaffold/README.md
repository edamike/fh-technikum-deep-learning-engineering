# Section 2 — Testing & Evaluation · Scaffold

Test **your** structured multi-agent system from Section 1 on three layers.

## Setup

Replace `my_agent/` with your agent from Section 1 (keep the folder name
`my_agent`, or rename it and update the imports in `tests/`).

## Your task

**Layer 1 — deterministic (no LLM):**
- `tests/test_tools.py` — mock the HTTP layer, test happy path, bad input, API errors
- `tests/test_schema.py` — one valid output + one invalid case per constraint
- `tests/test_agent_wiring.py` — assert which agent owns which tools

**Layers 2 + 3 — golden dataset (`evals/`):**
- `my_agent.test.json` — add at least: 2 happy-path cases, 2 edge cases
  (other language, ambiguous request, unusual input), 1 negative case
  (request the agent should refuse or ask about)
- `test_config.json` — write 3 rubrics a judge can check objectively

## Run

```bash
cd lecture6/02_testing_evaluation/scaffold

# deterministic tests
../../../.venv/bin/pytest

# LLM evaluation (needs GEMINI_API_KEY for the judge)
RUN_LLM_EVALS=1 ../../../.venv/bin/pytest -m llm -s
```

`tests/test_eval.py` is complete — it runs every `*.test.json` in `evals/`.

## Tip

Run the eval, read the failing rubric's rationale, fix the agent, and rerun.
That loop is the point of this exercise.
