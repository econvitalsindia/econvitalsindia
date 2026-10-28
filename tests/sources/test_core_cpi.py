"""Core CPI reproduces RBI's published core (Bulletin Table 19(c), Aug 2026 issue).

Inputs are MoSPI's published component indices for the four months RBI reports.
"""
import pandas as pd
import pytest
import yaml

from pipelines.sources.derived.core_cpi import WEIGHTS, compute
from tests.conftest import FIXTURES

RBI_CORE = {"2025-06-01": 103.31, "2025-07-01": 103.62, "2026-06-01": 107.34, "2026-07-01": 107.62}


def test_core_matches_rbi():
    indices = pd.read_csv(FIXTURES / "derived" / "cpi_components_rbi_check.csv", index_col=0)
    out = compute(indices, yaml.safe_load(WEIGHTS.read_text()))
    core = out[out.series_id == "cpi_core_index"].set_index("period")["value"]
    for period, rbi in RBI_CORE.items():
        assert core[period] == pytest.approx(rbi, abs=0.015), period


def test_weights_sum_to_100():
    w = yaml.safe_load(WEIGHTS.read_text())
    total = w["food_and_beverages"] + w["core"] + w["electricity_gas_fuels"] + w["vehicle_fuels"]
    assert total == pytest.approx(100, abs=0.01)
