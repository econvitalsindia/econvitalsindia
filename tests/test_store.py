"""Upsert semantics: add new periods, log revisions, keep absent periods and old vintages."""
import pandas as pd

from pipelines.core import store


def test_upsert(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "SERIES", tmp_path)
    pd.DataFrame({"period": ["2026-01-01", "2026-02-01"], "value": [1.0, 2.0],
                  "vintage": ["2026-02-10", "2026-03-10"], "note": ["", ""]}).to_csv(
        tmp_path / "x.csv", index=False)
    new = pd.DataFrame({"period": ["2026-02-01", "2026-03-01"], "value": [2.5, 3.0]})
    merged, revised = store.upsert("x", new, "2026-04-10")
    assert merged.period.tolist() == ["2026-01-01", "2026-02-01", "2026-03-01"]
    assert merged.value.tolist() == [1.0, 2.5, 3.0]
    assert merged.set_index("period").loc["2026-01-01", "vintage"] == "2026-02-10"
    assert revised.period.tolist() == ["2026-02-01"] and revised.old_value.iloc[0] == 2.0


def test_upsert_unchanged_keeps_vintage(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "SERIES", tmp_path)
    pd.DataFrame({"period": ["2026-01-01"], "value": [1.0], "vintage": ["2026-02-10"],
                  "note": [""]}).to_csv(tmp_path / "x.csv", index=False)
    merged, revised = store.upsert("x", pd.DataFrame({"period": ["2026-01-01"], "value": [1.0]}),
                                   "2026-04-10")
    assert merged.vintage.tolist() == ["2026-02-10"] and revised.empty
