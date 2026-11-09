"""Layer 1 — deterministic tests for the output contract.

Constrained decoding guarantees the shape of the JSON. These tests pin down the
rules we rely on downstream, so a schema change that breaks consumers is caught
in CI — without calling the model.
"""

import copy

import pytest
from pydantic import ValidationError

from travel_planner.agent import TravelPlan

VALID_PLAN = {
    "destination": "Graz, Austria",
    "days": [
        {
            "date": "2026-11-10",
            "condition": "Partly cloudy",
            "temp_min_c": 6.0,
            "temp_max_c": 14.0,
            "activities": [
                {"name": "Schlossberg", "category": "outdoor",
                 "weather_dependent": True, "estimated_cost_eur": 0},
            ],
        }
    ],
    "packing_list": ["Umbrella", "Warm jacket", "Walking shoes"],
    "risk_level": "low",
    "summary": "Mild autumn day, good for walking.",
}


def _with(path, value):
    plan = copy.deepcopy(VALID_PLAN)
    target = plan
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return plan


def test_valid_plan_is_accepted():
    plan = TravelPlan.model_validate(VALID_PLAN)
    assert plan.days[0].activities[0].category == "outdoor"


@pytest.mark.parametrize(
    "path, bad_value",
    [
        (("risk_level",), "extreme"),                                     # not in Literal
        (("days", 0, "activities", 0, "category"), "shopping"),           # not in Literal
        (("days", 0, "activities", 0, "estimated_cost_eur"), -5),        # below ge=0
        (("days", 0, "temp_max_c"), 80),                                  # above le=60
        (("days", 0, "date"), "next Tuesday"),                            # field_validator
        (("days", 0, "activities"), []),                                  # min_length=1
        (("packing_list",), ["Umbrella"]),                                # min_length=3
        (("days",), []),                                                  # min_length=1
    ],
)
def test_invalid_plans_are_rejected(path, bad_value):
    with pytest.raises(ValidationError):
        TravelPlan.model_validate(_with(path, bad_value))


def test_schema_exposes_descriptions_to_the_model():
    schema = TravelPlan.model_json_schema()
    assert "description" in schema["properties"]["destination"]
    assert set(schema["properties"]["risk_level"]["enum"]) == {"low", "medium", "high"}
