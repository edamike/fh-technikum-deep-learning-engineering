"""Guardrails — plain Python functions registered as ADK callbacks.

Lecture 6 · Section 3: Security · SCAFFOLD

ADK callback contracts used here:

    before_agent_callback(callback_context) -> Content | None
        Return Content → the agent is skipped and Content is the answer.

    after_tool_callback(tool, args, tool_context, tool_response) -> dict | None
        Return a dict → it replaces what the LLM sees as the tool result.

Return None in both cases to change nothing.
"""

import re
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# TODO 1: write regular expressions for typical injection phrases.
#   Collect real attacks first (see README) and make sure normal requests like
#   "I want to ignore museums" are NOT matched.
INJECTION_PATTERNS: list[str] = []

REFUSAL = "I can only help with planning trips."


def looks_like_injection(text: str) -> bool:
    # TODO 1: return True if any pattern matches (case-insensitive)
    return False


def block_prompt_injection(callback_context: CallbackContext) -> Optional[types.Content]:
    """Input guardrail for DIRECT injection in the user's message.

    TODO 2:
      - read the user's text from callback_context.user_content.parts
      - if looks_like_injection(text): append an entry to
        callback_context.state["security_events"] and return
        types.Content(role="model", parts=[types.Part(text=REFUSAL)])
    """
    return None


def sanitize_reviews(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> Optional[dict]:
    """Tool-output guardrail for INDIRECT injection hidden in reviews.

    TODO 3:
      - only act when tool.name == "get_local_reviews"
      - drop every review whose text looks like an injection or contains a URL
      - log removed reviews to tool_context.state["security_events"]
      - return the cleaned response (optionally with a note that reviews are
        untrusted opinions)
    """
    return None
