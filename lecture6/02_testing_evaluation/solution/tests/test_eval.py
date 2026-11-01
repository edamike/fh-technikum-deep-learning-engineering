"""Layers 2 + 3 — execution and semantic evaluation with a real LLM.

Runs the golden dataset in evals/ through ADK's AgentEvaluator:
  - tool_trajectory_avg_score              did the agent call the right specialists, in order?
  - rubric_based_final_response_quality_v1 LLM-as-a-judge scores the final plan against rubrics

Skipped by default. Run with:  RUN_LLM_EVALS=1 pytest -m llm
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
async def test_golden_dataset():
    eval_set = EvalSet.model_validate_json((EVAL_DIR / "travel_planner.test.json").read_text())
    await AgentEvaluator.evaluate_eval_set(
        agent_module="travel_planner",
        eval_set=eval_set,
        eval_config=_eval_config(),
        num_runs=1,
        print_detailed_results=True,
    )
