"""Weather Agent — LangChain Ecosystem Showcase.

Lecture 7 · FH Technikum Wien — Deep Learning Engineering / AI Agents Course.

Demonstrates four pieces of the LangChain ecosystem working together:

- **LangChain**  — tool decorator (`@tool`), chat-model abstraction
- **LangGraph**  — stateful ReAct agent compiled from a graph via
                   `create_react_agent` (nodes = agent + tools, conditional edges)
- **LangSmith**  — automatic tracing when `LANGSMITH_TRACING=true` and
                   `LANGSMITH_API_KEY` are set in `.env`. View every LLM/tool
                   call at https://smith.langchain.com — no code change needed.
- **LangFlow**   — visual drag-and-drop flow builder. After `pip install langflow`,
                   run `langflow run` and open http://localhost:7860 to build
                   the same agent in the browser.

Run:
    cd lecture7/01_langchain
    python agent.py
"""

import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools.weather_tool import get_weather_forecast as _fetch_weather


# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()


# ── Observability (LangSmith) ─────────────────────────────────────────────────
# LangChain auto-instruments the whole run when these env vars are present —
# every LLM call, tool call, and intermediate state is pushed to LangSmith.
#   LANGSMITH_TRACING=true
#   LANGSMITH_API_KEY=lsv2_pt_...
#   LANGSMITH_PROJECT=fh-lecture7-langchain   # optional, groups traces
_LANGSMITH_ON = os.getenv("LANGSMITH_TRACING", "").lower() == "true"


# ── Tool Definition ───────────────────────────────────────────────────────────
# LangChain infers the JSON schema from the function signature & docstring.

@tool
def get_weather_forecast(location: str, days: int = 3) -> str:
    """Retrieve the current weather and a multi-day forecast for a location.

    Args:
        location: City or region name, e.g. 'Vienna', 'Berlin', 'New York'.
        days: Number of forecast days (1–7, default 3).
    """
    result = _fetch_weather(location, days)
    return json.dumps(result, indent=2)


# ── Model selection ───────────────────────────────────────────────────────────
# Set USE_LOCAL_LLM=true + OPENAI_API_KEY + OPENAI_BASE_URL in .env to switch
# to the FH Lion endpoint (Qwen3.6-35B-A3B, OpenAI-compatible).

def _get_llm():
    if os.getenv("USE_LOCAL_LLM", "true").lower() == "true":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("LION_MODEL", "Qwen/Qwen3.6-35B-A3B"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        )
    return ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

# ── Model & Agent (LangGraph) ─────────────────────────────────────────────────
# `create_react_agent` returns a compiled LangGraph: nodes = agent + tools,
# conditional edges route to tools when a `tool_call` is produced, else END.

llm = _get_llm()


def _ensure_user_message(state):
    # Lion's vLLM endpoint rejects any `chat/completions` request whose
    # final message list has no `role: user` turn — "No user query found
    # in messages." (HTTP 400). This happens when either (a) Studio
    # submits an empty run before the user types, or (b) the ReAct loop
    # re-enters the model node after a `tool` message so the last turn
    # is a ToolMessage. Returning `llm_input_messages` overrides what the
    # model node sees without rewriting the stored thread state.
    msgs = list(state.get("messages", []))
    has_human = any(getattr(m, "type", None) == "human" for m in msgs)
    if not has_human:
        msgs.append(HumanMessage(content="Hello — what can you do?"))
    return {"llm_input_messages": msgs}


root_agent = create_react_agent(
    model=llm,
    tools=[get_weather_forecast],
    prompt=(
        "You are a friendly Meteorological AI Assistant created for "
        "FH Technikum Wien students.\n\n"
        "ALWAYS use the `get_weather_forecast` tool when a user asks about "
        "weather. Default to 3 forecast days if not specified.\n"
        "Present results clearly: location, current conditions, daily "
        "forecast table, and practical advice (umbrella, jacket, etc.)."
    ),
    pre_model_hook=_ensure_user_message,
)


# ── Interactive CLI Loop ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    _local = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
    _model_name = "Qwen3.6-35B-A3B (Lion)" if _local else "Gemini 3.8 Flash"
    print("🌦️  Weather Agent — LangChain ecosystem (LangChain · LangGraph · LangSmith · LangFlow)")
    print(f"   Model:    {_model_name}")
    print(f"   Tracing:  LangSmith {'ON' if _LANGSMITH_ON else 'off (set LANGSMITH_TRACING=true)'}")
    print(f"   Visual:   run `langflow run` in another terminal → http://localhost:7860")
    print("=" * 60)
    try:
        print("\nLangGraph structure:\n")
        print(root_agent.get_graph().draw_mermaid())
    except Exception:  # noqa: BLE001 — purely decorative
        pass
    print("Type your question (or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("[user]: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        response = root_agent.invoke({"messages": [("human", user_input)]})

        for msg in reversed(response["messages"]):
            if msg.type == "ai" and msg.content:
                print(f"\n[agent]: {msg.content}\n")
                break


if __name__ == "__main__":
    main()
