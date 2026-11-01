# Lecture 6 — Reliability, Evaluation and Security

**Deep Learning Engineering · FH Technikum Wien**

Builds on the multi-agent system from Lecture 5 · Section 3.

| Section | Concept |
|---------|---------|
| `01_constrained_decoding` | Force the final answer into a Pydantic schema (`output_schema`) |
| `02_testing_evaluation` | Deterministic tests, tool-trajectory evals, LLM-as-a-judge |
| `03_security` | Prompt injection attacks, guardrail callbacks, red-team evals |

Each section has:
- **`scaffold/`** — starter code with `# TODO` markers, domain-agnostic
- **`solution/`** — complete reference implementation (travel planner)

Every folder has its own README with exact run commands.

## Setup

```bash
# from the repo root
pip install -r requirements.txt
cp .env.example .env     # OPENAI_API_KEY (FH Lion default); set USE_LOCAL_LLM=false + GEMINI_API_KEY to use Gemini
```

## Quick start

```bash
# Section 1 — structured output in the web UI
.venv/bin/adk web lecture6/01_constrained_decoding

# Section 2 — deterministic tests (no LLM)
cd lecture6/02_testing_evaluation/solution && ../../../.venv/bin/pytest

# Section 2 — LLM evaluation (judge needs GEMINI_API_KEY)
RUN_LLM_EVALS=1 ../../../.venv/bin/pytest -m llm -s

# Section 3 — attack the agent in the browser (scaffold = vulnerable, solution = guarded)
cd ../../.. && .venv/bin/adk web lecture6/03_security
```
