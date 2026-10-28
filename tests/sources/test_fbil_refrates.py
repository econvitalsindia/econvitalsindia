"""FBIL 12-month reference-rate history."""
from pipelines.sources.fbil.refrates import SOURCE


def test_parse_history(raw_from):
    df = SOURCE.parse([raw_from("fbil/refrates/2026-10-28.json")])
    assert set(df.series_id) == {"usdinr_ref"}
    assert len(df) == 240
    latest = df.sort_values("period").iloc[-1]
    assert latest.period == "2026-10-19" and latest.value == 94.7691
