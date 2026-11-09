"""Layers 2 + 3 — execution and semantic evaluation with a real LLM.

Runs every *.test.json file in evals/ through ADK's AgentEvaluator using the
criteria in evals/test_config.json. This file is complete — your work is in
evals/.

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
        for criterion in config["criteria"].values():
            if isinstance(criterion, dict) and "judge_model_options" in criterion:
                criterion["judge_model_options"]["judge_model"] = judge_model
    return EvalConfig.model_validate(config)


@pytest.mark.llm
@pytest.mark.asyncio
@pytest.mark.parametrize("eval_file", sorted(EVAL_DIR.glob("*.test.json")), ids=lambda p: p.name)
async def test_eval_set(eval_file):
    await AgentEvaluator.evaluate_eval_set(
        agent_module="my_agent",
        eval_set=EvalSet.model_validate_json(eval_file.read_text()),
        eval_config=_eval_config(),
        num_runs=1,
        print_detailed_results=True,
    )
