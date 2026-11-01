# Section 2 — Testing & Evaluation · Solution

The structured travel planner from Section 1, tested on the three layers from
the lecture.

| Layer | File | LLM? | What it checks |
|---|---|---|---|
| Deterministic | `tests/test_tools.py` | no | Tool parses the API, clamps input, survives errors (HTTP mocked) |
| Deterministic | `tests/test_schema.py` | no | Output contract: valid plan accepted, every constraint rejects bad data |
| Deterministic | `tests/test_agent_wiring.py` | no | Agent graph: who has which tools, where the schema is enforced |
| Execution | `evals/travel_planner.test.json` | yes | `tool_trajectory_avg_score`: specialists called in the right order |
| Semantic | `evals/test_config.json` | yes | `rubric_based_final_response_quality_v1`: LLM-as-a-judge with rubrics |

ADK also reports `tool_call_count_v1`, `inference_call_count_v1`,
`token_usage_v1` and `invocation_duration_v1` for every case — the
observability metrics from the slides.

## Prerequisites

```bash
# from the repo root
pip install -r requirements.txt    # includes google-adk[eval], pytest, pytest-asyncio
cp .env.example .env
```

## 1. Deterministic tests (fast, free, no API key needed)

```bash
cd lecture6/02_testing_evaluation/solution
../../../.venv/bin/pytest
```

Expected: `18 passed, 1 skipped` (the skipped one is the LLM evaluation).

## 2. LLM evaluation with pytest

```bash
cd lecture6/02_testing_evaluation/solution
RUN_LLM_EVALS=1 ../../../.venv/bin/pytest -m llm -s
```

Runs the three golden-dataset cases (~1 min each).

**Judge model:** `gemini-3.8-flash` by default, so `GEMINI_API_KEY` must be set
even though the agent itself runs on FH Lion. Qwen on Lion writes its
reasoning into the answer text, which breaks ADK's judge-output parser.
A different, stronger model as judge is better practice anyway.
Override with `JUDGE_MODEL=<model>`.

## 3. LLM evaluation with the ADK CLI

```bash
# from the repo root
.venv/bin/adk eval lecture6/02_testing_evaluation/solution/travel_planner \
    lecture6/02_testing_evaluation/solution/evals/travel_planner.test.json \
    --config_file_path lecture6/02_testing_evaluation/solution/evals/test_config.json
```

Run a single case by appending `:<eval_id>` to the eval set path, e.g.
`travel_planner.test.json:happy_path_vienna_3_days`.

## 4. Inspect in the web UI

```bash
.venv/bin/adk web lecture6/02_testing_evaluation/solution
```

Select `travel_planner` to chat with the same agent the tests cover.
