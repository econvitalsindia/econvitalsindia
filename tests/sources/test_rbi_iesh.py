"""RBI household inflation expectations, Table 3 medians."""
from pipelines.sources.rbi.iesh import SOURCE


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_iesh(raw_from):
    df = SOURCE.parse([raw_from("rbi/iesh/iesh_latest.pdf")])
    assert at(df, "iesh_current_perception", "2026-09-01") == 8.4
    assert at(df, "iesh_3m_ahead", "2026-09-01") == 9.9
    assert at(df, "iesh_1y_ahead", "2026-09-01") == 10.0
    assert at(df, "iesh_1y_ahead", "2025-09-01") == 8.7
