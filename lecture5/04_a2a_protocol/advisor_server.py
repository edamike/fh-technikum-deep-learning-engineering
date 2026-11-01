"""Activity advisor exposed as an A2A service.

Lecture 5 · Section 4: A2A Protocol · SOLUTION
──────────────────────────────────────────────
Second A2A server — pairs with `weather_server.py`. Publishes:
    http://localhost:8002/.well-known/agent-card.json

Run (from this directory):
    python advisor_server.py
"""

import uvicorn

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from specialists import activity_advisor

HOST = "localhost"
PORT = 8002

app = to_a2a(activity_advisor, host=HOST, port=PORT)


if __name__ == "__main__":
    print(f"🎒 activity_advisor → http://{HOST}:{PORT}")
    print(f"   agent card       → http://{HOST}:{PORT}/.well-known/agent-card.json")
    uvicorn.run(app, host=HOST, port=PORT)
