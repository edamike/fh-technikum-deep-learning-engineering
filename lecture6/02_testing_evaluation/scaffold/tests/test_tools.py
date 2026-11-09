"""Layer 1 — deterministic tests for your tool(s).

No LLM, no network. Replace the HTTP layer with a fake so the test is fast,
free and gives the same result every time.

One example is complete — write the TODO tests for YOUR tool.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from my_agent.tools import weather_tool
from my_agent.tools.weather_tool import get_weather_forecast


@patch.object(weather_tool.requests, "get", side_effect=requests.ConnectionError("offline"))
def test_example_tool_survives_network_failure(_):
    result = get_weather_forecast("Vienna", days=2)
    assert len(result["forecast"]) == 2


def test_happy_path_parses_api_response():
    # TODO: fake a successful API response (MagicMock with status_code=200 and
    #       .json.return_value=...) and assert the tool returns the fields the
    #       agent relies on.
    pytest.skip("TODO")


def test_input_is_validated_or_clamped():
    # TODO: call the tool with an out-of-range argument and assert it is
    #       clamped or rejected — never forwarded blindly to the API.
    pytest.skip("TODO")


def test_api_error_does_not_crash_the_agent():
    # TODO: fake a 4xx/5xx response and assert the tool returns something the
    #       LLM can reason about instead of raising.
    pytest.skip("TODO")
