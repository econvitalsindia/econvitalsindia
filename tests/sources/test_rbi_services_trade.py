"""RBI monthly trade in services release (August 2026)."""
from pipelines.sources.rbi.services_trade import SOURCE


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_services(raw_from):
    df = SOURCE.parse([raw_from("rbi/services/2026-08.html")])
    assert at(df, "services_exports", "2026-08-01") == 35.471      # US$ bn
    assert at(df, "services_imports", "2026-08-01") == 18.934
    assert at(df, "services_exports_growth", "2026-08-01") == 13.7
    assert at(df, "services_exports", "2026-04-01") == 36.845      # revised earlier month
    assert set(df.period) >= {f"2026-0{m}-01" for m in range(4, 9)}
