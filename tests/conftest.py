import random
import sys
from pathlib import Path

import pytest

# Ensure project root is importable when running pytest via uv from any cwd
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game_engine import GameState  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_random_seed():
    random.seed(0)


@pytest.fixture
def game_state():
    return GameState()
