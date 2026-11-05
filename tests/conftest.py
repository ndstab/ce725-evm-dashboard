"""Shared fixtures.

The repository root is put on sys.path so the tests import the same `evm`
package the Streamlit app imports, with no install step. This keeps the
project runnable by a marker who has only cloned the repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import evm  # noqa: E402

DATA_DIR = ROOT / "data"

# Rupee tolerance for comparisons against hand calculations. The case study
# CSVs store planned value rounded to two decimal places, so aggregating
# nineteen work packages over twelve periods can drift by a few paise.
RUPEE_TOL = 1.0


SAMPLE_2_DIR = ROOT / "samples" / "case-02-water-treatment"


@pytest.fixture(scope="session")
def project() -> "evm.Project":
    return evm.load_project(DATA_DIR)


@pytest.fixture(scope="session")
def under_budget_project() -> "evm.Project":
    """A second case study that is behind programme but UNDER budget.

    The bundled case study is adverse on both axes, which leaves the
    favourable branches of the commentary and the forecast untested. This
    project exists to exercise them.
    """
    return evm.load_project(SAMPLE_2_DIR)
