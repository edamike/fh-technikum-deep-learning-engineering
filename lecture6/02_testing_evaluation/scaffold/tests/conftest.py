import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

SOLUTION_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SOLUTION_DIR.parents[2]

sys.path.insert(0, str(SOLUTION_DIR))
load_dotenv(REPO_ROOT / ".env")


def pytest_configure(config):
    config.addinivalue_line("markers", "llm: calls a real LLM (slow, costs tokens)")


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LLM_EVALS") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LLM_EVALS=1 to run LLM evaluations")
    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip)
