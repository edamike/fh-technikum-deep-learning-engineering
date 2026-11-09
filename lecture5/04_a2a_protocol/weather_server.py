"""Weather specialist exposed as an A2A service.

Lecture 5 · Section 4: A2A Protocol · SOLUTION
──────────────────────────────────────────────
`to_a2a(agent)` turns an ADK LlmAgent into a Starlette ASGI app that speaks
Google's open Agent-to-Agent protocol (JSON-RPC over HTTP + SSE). The app
also publishes an Agent Card at
    http://localhost:8001/.well-known/agent-card.json
which `RemoteA2aAgent` fetches to learn the agent's name, description and
capabilities before sending its first task.

Run (from this directory):
    python weather_server.py
"""

import uvicorn

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from specialists import weather_agent

HOST = "localhost"
PORT = 8001

app = to_a2a(weather_agent, host=HOST, port=PORT)


if __name__ == "__main__":
    print(f"🌦️  weather_agent → http://{HOST}:{PORT}")
    print(f"   agent card    → http://{HOST}:{PORT}/.well-known/agent-card.json")
    uvicorn.run(app, host=HOST, port=PORT)
