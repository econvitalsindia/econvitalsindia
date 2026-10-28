"""Checks on the committed data itself (not parsers): identities that must hold."""
import pandas as pd
import pytest
import yaml

from pipelines.core.store import ROOT, SERIES


def test_cpi_divisions_reproduce_headline():
    """CPI 2024 is fixed-weight: weighted divisions must equal the published general index."""
    w = yaml.safe_load((ROOT / "registry/weights/cpi2024_divisions.yaml").read_text())["weights"]
    assert sum(w.values()) == pytest.approx(100, abs=0.01)
    idx = pd.concat({s: pd.read_csv(SERIES / f"{s}.csv").set_index("period")["value"] for s in w}, axis=1).dropna()
    gen = pd.read_csv(SERIES / "cpi_headline_index.csv").set_index("period")["value"]
    implied = (idx * pd.Series(w)).sum(axis=1) / 100
    assert (implied - gen.reindex(implied.index)).abs().max() < 0.02


def test_direct_tax_is_corporate_plus_income():
    from pipelines.core.store import load_series
    get = lambda s: load_series(s).set_index("period")["value"].astype(float)
    direct, corp, inc = get("cga_direct_tax_fytd"), get("cga_corporate_tax_fytd"), get("cga_income_tax_fytd")
    assert len(direct) > 100
    assert ((corp + inc).loc[direct.index] - direct).abs().max() < 1e-3
