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


def test_upsert_unchanged_value_takes_new_note(tmp_path, monkeypatch):
    # An estimate moving from "Provisional" to "First Revised" at the same value: the note
    # updates, the vintage (first appearance) stays, and nothing is logged as a revision.
    monkeypatch.setattr(store, "SERIES", tmp_path)
    pd.DataFrame({"period": ["2025-04-01"], "value": [7.8], "vintage": ["2026-05-30"],
                  "note": ["Provisional Estimates"]}).to_csv(tmp_path / "x.csv", index=False)
    new = pd.DataFrame({"period": ["2025-04-01"], "value": [7.8], "note": ["First Revised Estimates"]})
    merged, revised = store.upsert("x", new, "2027-02-27")
    row = merged.iloc[0]
    assert (row.note, row.vintage) == ("First Revised Estimates", "2026-05-30") and revised.empty


def test_upsert_panel_unchanged_value_takes_new_note(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "PANELS", tmp_path)
    pd.DataFrame({"entity": ["Mining"], "period": ["2025-04-01"], "value": [3.0], "vintage": ["2026-05-30"],
                  "note": ["Provisional Estimates"]}).to_csv(tmp_path / "p.csv", index=False)
    new = pd.DataFrame({"entity": ["Mining"], "period": ["2025-04-01"], "value": [3.0], "note": ["Final Estimates"]})
    merged = store.upsert_panel("p", new, "2027-02-27")
    assert (merged.iloc[0].note, merged.iloc[0].vintage) == ("Final Estimates", "2026-05-30")
