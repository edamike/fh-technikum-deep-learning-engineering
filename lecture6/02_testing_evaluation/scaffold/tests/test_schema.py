"""Layer 1 — deterministic tests for your output schema.

Constrained decoding guarantees the SHAPE of the JSON. These tests pin down the
rules downstream consumers rely on — without calling the model.

Rename TravelPlan to your schema class from Section 1.
"""

import pytest
from pydantic import ValidationError

from my_agent.agent import TravelPlan

VALID_OUTPUT: dict = {
    # TODO: paste one realistic, valid output of your agent here
    #       (copy it from the State tab in `adk web`).
}


def test_valid_output_is_accepted():
    if not VALID_OUTPUT:
        pytest.skip("TODO: fill VALID_OUTPUT")
    TravelPlan.model_validate(VALID_OUTPUT)


@pytest.mark.parametrize(
    "field, bad_value",
    [
        # TODO: one row per constraint in your schema, e.g.
        # ("risk_level", "extreme"),     # value outside a Literal
        # ("packing_list", []),          # violates min_length
    ],
)
def test_invalid_outputs_are_rejected(field, bad_value):
    output = {**VALID_OUTPUT, field: bad_value}
    with pytest.raises(ValidationError):
        TravelPlan.model_validate(output)
