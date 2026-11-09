"""Red-teaming as an evaluation — attacks run end to end against the real agent.

Every case in evals/security.test.json is an attack (plus one regression case).
An LLM judge checks the answers against security rubrics in test_config.json.

Run it BEFORE and AFTER adding your guardrails and compare.
This file is complete — your work is in evals/.

Skipped by default. Run with:  RUN_LLM_EVALS=1 pytest -m llm -s
"""

import json
import os
from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_set import EvalSet

EVAL_DIR = Path(__file__).resolve().parents[1] / "evals"


def _eval_config() -> EvalConfig:
    config = json.loads((EVAL_DIR / "test_config.json").read_text())
    if judge_model := os.getenv("JUDGE_MODEL"):
        judge = config["criteria"]["rubric_based_final_response_quality_v1"]["judge_model_options"]
        judge["judge_model"] = judge_model
    return EvalConfig.model_validate(config)


@pytest.mark.llm
@pytest.mark.asyncio
async def test_red_team_dataset():
    await AgentEvaluator.evaluate_eval_set(
        agent_module="my_agent",
        eval_set=EvalSet.model_validate_json((EVAL_DIR / "security.test.json").read_text()),
        eval_config=_eval_config(),
        num_runs=1,
        print_detailed_results=True,
    )
