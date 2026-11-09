# Lecture 7 — Multi-Framework Comparison

**Deep Learning Engineering · FH Technikum Wien**

The *same* weather forecast agent built in three frameworks, so students can
compare how each one handles tool registration, agent configuration, and the
execution loop.

| Section | Framework | Model | Key API |
|---------|-----------|-------|---------|
| `01_langchain` | LangChain · LangGraph · LangSmith · LangFlow | FH Lion / Gemini | `@tool`, `create_react_agent`, LangSmith tracing, LangFlow UI |
| `02_crewai` | CrewAI | FH Lion / Gemini (via LiteLLM) | `Agent` + `Task` + `Crew.kickoff()` |
| `03_openai_agents` | OpenAI Agents SDK | OpenAI | `@function_tool`, `Runner.run()` |

All three share the same tool logic (`tools/weather_tool.py`) calling the
Open-Meteo public API.

---

## Quick start

From the repo root, after installing the framework you want (see Setup below):

```bash
# LangChain + LangGraph + LangSmith + LangFlow
(cd lecture7/01_langchain && ../../.venv/bin/python agent.py)

# CrewAI
(cd lecture7/02_crewai && ../../.venv/bin/python agent.py)

# OpenAI Agents SDK
(cd lecture7/03_openai_agents && ../../.venv/bin/python agent.py)

# LangFlow visual builder (requires langflow installed)
.venv/bin/langflow run       # then open http://127.0.0.1:7860
```

Each CLI opens an interactive prompt — type a weather question, `exit` to quit.

---

## Setup

```bash
# from the repo root — install the framework you want to try
pip install -r lecture7/01_langchain/requirements.txt
pip install -r lecture7/02_crewai/requirements.txt
pip install -r lecture7/03_openai_agents/requirements.txt
```

Create a `.env` file in each section you want to run (defaults to FH Lion):

```bash
# lecture7/01_langchain/.env and lecture7/02_crewai/.env
OPENAI_API_KEY=your_lion_api_key_here
OPENAI_BASE_URL=https://lion.aida.cs.technikum-wien.at/v1

# Optional: enable LangSmith tracing for Section 1
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=fh-lecture7-langchain

# lecture7/03_openai_agents/.env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## Run

```bash
# Section 1 — LangChain ecosystem (CLI)
cd lecture7/01_langchain && python agent.py

# Section 1b — LangFlow visual builder (requires langflow installed)
langflow run                 # then open http://localhost:7860

# Section 2 — CrewAI
cd lecture7/02_crewai && python agent.py

# Section 3 — OpenAI Agents SDK
cd lecture7/03_openai_agents && python agent.py
```

### LangChain ecosystem (Section 1)

The LangChain example exercises four pieces of the ecosystem in one file:

- **LangChain** — `@tool` decorator, `ChatOpenAI` / `ChatGoogleGenerativeAI`.
- **LangGraph** — `create_react_agent` compiles a graph (agent + tools nodes,
  conditional edges). The agent prints its graph on startup via
  `get_graph().draw_mermaid()`.
- **LangSmith** — set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `.env`
  to send every LLM call and tool call to https://smith.langchain.com. No code
  change needed; LangChain auto-instruments.
- **LangFlow** — standalone drag-and-drop UI. After `pip install langflow`,
  run `langflow run` and build the same agent visually at
  http://localhost:7860.

---

## Framework comparison

| Aspect | LangChain + LangGraph | CrewAI | OpenAI Agents SDK |
|--------|----------------------|--------|-------------------|
| Tool decorator | `@tool` | `@tool` | `@function_tool` |
| Agent class | `create_react_agent()` | `Agent(role, goal, …)` | `Agent(name, instructions, …)` |
| Execution | `agent.invoke({"messages": …})` | `Crew.kickoff()` | `await Runner.run(agent, input)` |
| Async | Optional | No | Yes (native) |
| Model provider | Pluggable (Gemini, OpenAI, …) | Pluggable via LiteLLM | OpenAI-native |
| Multi-agent | LangGraph workflows | Crew + Process orchestration | Agent handoffs |
| Abstraction | Low-level, composable | High-level, role-based | Minimal, opinionated |
| Schema source | Docstring + type hints | Docstring + type hints | Docstring + type hints |

### Takeaways

1. **Tool registration is nearly identical** across all three — Python type hints and docstrings are the universal schema language.
2. **CrewAI is the most opinionated**: you think in *roles*, *goals*, and *tasks* rather than raw prompts.
3. **LangChain is the most flexible**: the LangGraph layer lets you build arbitrary state machines, not just ReAct loops.
4. **OpenAI Agents SDK is the simplest**: minimal API surface, but locked to OpenAI models out of the box.
5. **The underlying pattern is always the same**: prompt → LLM decides to call tool → tool runs → LLM synthesises response.

---

## Student exercises

1. Add structured output (like Lecture 6 · Section 1) to each framework — compare how each handles JSON response schemas.
2. Add a second tool (e.g. air quality) and observe how each framework handles multi-tool selection.
3. Benchmark: run the same query on all three and compare latency, token usage, and response quality.
