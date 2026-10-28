"""Canonical state names and panel upserts."""
import pandas as pd
import pytest

from pipelines.core import store
from pipelines.core.states import canonical


def test_canonical_names():
    assert canonical("NCT of Delhi") == "Delhi"
    assert canonical("Andaman & Nicobar Islands") == "Andaman and Nicobar Islands"
    assert canonical("The Dadra And Nagar Haveli And Daman And Diu") == "Dadra and Nagar Haveli and Daman and Diu"
    assert canonical("All India") is None
    with pytest.raises(ValueError):
        canonical("Atlantis")


def test_panel_upsert(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "PANELS", tmp_path)
    pd.DataFrame({"entity": ["Goa", "Goa"], "period": ["2025-01-01", "2026-01-01"], "value": [1.0, 2.0],
                  "vintage": ["2026-01-10", "2026-02-10"], "note": ["", ""]}).to_csv(tmp_path / "x.csv", index=False)
    new = pd.DataFrame({"entity": ["Goa", "Goa", "Bihar"], "period": ["2025-01-01", "2026-01-01", "2026-01-01"],
                        "value": [1.0, 2.5, 3.0]})
    out = store.upsert_panel("x", new, "2026-03-10").set_index(["entity", "period"])
    assert out.loc[("Goa", "2025-01-01"), "vintage"] == "2026-01-10"    # unchanged keeps first vintage
    assert out.loc[("Goa", "2026-01-01"), "value"] == 2.5               # revised
    assert out.loc[("Bihar", "2026-01-01"), "value"] == 3.0             # added
