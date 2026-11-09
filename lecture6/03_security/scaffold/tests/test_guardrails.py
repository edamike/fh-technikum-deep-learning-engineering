"""Deterministic security tests — no LLM.

Guardrails are plain functions, so they can be tested like any other code.
Two tests are complete; they fail until guardrails.py is implemented.
"""

from types import SimpleNamespace

import pytest

from my_agent.guardrails import block_prompt_injection, looks_like_injection, sanitize_reviews
from my_agent.tools import get_local_reviews


def test_poisoned_review_is_removed():
    tool = SimpleNamespace(name="get_local_reviews")
    raw = get_local_reviews("Salzburg")
    clean = sanitize_reviews(tool, {"city": "Salzburg"}, SimpleNamespace(state={}), raw)

    assert clean is not None, "sanitize_reviews returned None — implement TODO 3"
    assert not any("example.com" in r["text"] for r in clean["reviews"])


@pytest.mark.parametrize("text", ["Plan a 3 day trip to Vienna", "I want to ignore museums"])
def test_normal_requests_are_not_flagged(text):
    assert not looks_like_injection(text)


def test_known_attacks_are_flagged():
    # TODO: parametrize with attack strings you collected and assert they are detected
    pytest.skip("TODO")


def test_input_guardrail_refuses_attacks():
    # TODO: build a fake callback_context with SimpleNamespace(user_content=..., state={})
    #       and assert block_prompt_injection returns a refusal for an attack
    _ = block_prompt_injection
    pytest.skip("TODO")


def test_guardrails_are_registered():
    # TODO: import my_agent.agent and assert the callbacks are wired to the right agents
    pytest.skip("TODO")
