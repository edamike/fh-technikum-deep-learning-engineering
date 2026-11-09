"""Layer 1 — deterministic tests for the agent graph.

These guard architectural decisions (and security scoping) without an LLM:
which agent may call which tools, and where the schema is enforced.
"""

from google.adk.agents import SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from travel_planner.agent import TravelPlan, root_agent


def _by_name(name):
    agent = root_agent.find_agent(name)
    assert agent is not None, f"agent {name!r} missing"
    return agent


def test_pipeline_order():
    assert isinstance(root_agent, SequentialAgent)
    assert [a.name for a in root_agent.sub_agents] == ["researcher", "formatter"]


def test_researcher_calls_specialists_as_tools():
    researcher = _by_name("researcher")
    tool_names = {t.agent.name for t in researcher.tools if isinstance(t, AgentTool)}
    assert tool_names == {"weather_agent", "activity_advisor"}
    assert researcher.output_key == "research_notes"


def test_formatter_is_constrained_and_has_no_tools():
    formatter = _by_name("formatter")
    assert formatter.output_schema is TravelPlan
    assert formatter.tools == []
    assert "{research_notes}" in formatter.instruction


def test_only_weather_agent_has_network_access():
    specialists = {t.agent.name: t.agent for t in _by_name("researcher").tools}
    weather, advisor = specialists["weather_agent"], specialists["activity_advisor"]
    assert [t.__name__ for t in weather.tools] == ["get_weather_forecast"]
    assert advisor.tools == []
