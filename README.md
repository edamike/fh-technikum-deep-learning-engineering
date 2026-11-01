# fh-technikum-deep-learning-engineering

Course material for the FH Technikum Wien course **Deep Learning Engineering**.

Hands-on exercises for the AI Agents lectures of the course, built around the
**Google Agent Development Kit (ADK)** and a multi-framework comparison.
Each exercise ships with a `scaffold/` (starter code with `# TODO` markers) and
a `solution/` (complete reference implementation).

## Lectures

| Lecture | Topic | Framework |
|---------|-------|-----------|
| [Lecture 5](lecture5/README.md) — Agent Architecture | Single agent, session persistence, multi-agent orchestration | Google ADK |
| [Lecture 6](lecture6/README.md) — Reliability, Evaluation and Security | Constrained decoding, deterministic + LLM-judge evals, prompt-injection guardrails | Google ADK |
| [Lecture 7](lecture7/README.md) — Multi-Framework Comparison | Same agent built three ways: LangChain, CrewAI, OpenAI Agents SDK | LangChain · CrewAI · OpenAI Agents |

Each lecture has its own README with the exact run commands for every section.

---

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/edamike/fh-technikum-deep-learning-engineering.git
cd fh-technikum-deep-learning-engineering

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate            # Linux/macOS
# .venv\Scripts\activate              # Windows

# 3. Install the core ADK dependencies (Lecture 5 & 6)
pip install -r requirements.txt

# 4. Install Lecture 7 per framework when you need it
pip install -r lecture7/01_langchain/requirements.txt
pip install -r lecture7/02_crewai/requirements.txt
pip install -r lecture7/03_openai_agents/requirements.txt
```

## API keys

Copy `.env.example` to `.env` and fill in the keys you need:

```bash
cp .env.example .env
```

The default model across all lectures is **FH Lion** (Qwen3.6-35B-A3B,
OpenAI-compatible endpoint) — the key is distributed to students as part of
the course. Set `USE_LOCAL_LLM=false` to switch to Google Gemini instead.

| Variable | Used by | How to get it |
|----------|---------|---------------|
| `OPENAI_API_KEY` | **Default** — FH Lion (Lectures 5, 6, 7 LangChain + CrewAI); or OpenAI itself for Lecture 7 OpenAI Agents SDK | FH Technikum Wien, or OpenAI dashboard |
| `OPENAI_BASE_URL` | FH Lion endpoint URL (preset in `.env.example`) | — |
| `USE_LOCAL_LLM` | `true` (default) → FH Lion; `false` → Gemini (Lectures 5 & 6) | — |
| `GEMINI_API_KEY` | Only needed when `USE_LOCAL_LLM=false`, or for the LLM-judge in Lecture 6 · Section 2 | https://aistudio.google.com/app/api-keys |
| `DATABASE_URL` | Lecture 5 · Section 2 (PostgreSQL session persistence) | — |

---

## Running an ADK agent

ADK agents (Lectures 5 & 6) can be launched in two modes.

### Terminal CLI

```bash
adk run <path/to/agent_dir>
# e.g. adk run lecture5/01_single_agent/solution
```

### Web UI

```bash
adk web <path/to/agents_parent>
# e.g. adk web lecture5/01_single_agent
```

Then open http://localhost:8000.

To use PostgreSQL for session persistence (Lecture 5 · Section 2):

```bash
adk web lecture5/02_add_persistence \
  --session_service_uri="postgresql+asyncpg://adk_user:adk_password@localhost:5432/adk_sessions"
```

---

## Repository layout

```
.
├── README.md                 # This file
├── requirements.txt          # Shared ADK dependencies
├── .env.example              # Environment template
├── lecture5/                 # Agent architecture (ADK)
│   ├── 01_single_agent/
│   ├── 02_add_persistence/
│   ├── 03_multi_agent/
│   └── 04_a2a_protocol/      # same orchestration over Google's A2A protocol
├── lecture6/                 # Reliability, evaluation, security (ADK)
│   ├── 01_constrained_decoding/
│   ├── 02_testing_evaluation/
│   └── 03_security/
└── lecture7/                 # Multi-framework comparison
    ├── 01_langchain/
    ├── 02_crewai/
    └── 03_openai_agents/
```

Every section under `lecture5/` and `lecture6/` contains `scaffold/`
(for the lecture) and `solution/` (released afterwards).
