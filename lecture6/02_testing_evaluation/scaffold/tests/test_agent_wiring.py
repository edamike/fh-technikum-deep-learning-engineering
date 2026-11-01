"""Layer 1 — deterministic tests for the agent graph.

Guard architectural decisions without an LLM: which agent may call which
tools, and where the schema is enforced. These tests also protect against
"excessive agency" — an agent silently gaining a tool it should not have.
"""

import pytest

from my_agent.agent import root_agent


def test_pipeline_order():
    assert [a.name for a in root_agent.sub_agents] == ["researcher", "formatter"]


def test_formatter_is_constrained_and_has_no_tools():
    # TODO: assert the formatter has an output_schema and no tools.
    #       Hint: root_agent.find_agent("formatter")
    pytest.skip("TODO")


def test_specialists_have_only_the_tools_they_need():
    # TODO: list the specialists behind the researcher's AgentTools
    #       (tool.agent) and assert each one has exactly the tools you expect.
    pytest.skip("TODO")
