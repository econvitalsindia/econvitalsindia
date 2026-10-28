"""GST workbook: levels from each month's own sheet; malformed Jan-25 sheet skipped."""
from pipelines.sources.gst.collections import SOURCE, month_of


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_gst(raw_from):
    df = SOURCE.parse([raw_from("gst/gross_net_2026-10.xlsx")])
    assert at(df, "gst_gross_collections", "2026-08-01") == 1.9985   # ₹ lakh crore
    assert at(df, "gst_gross_growth", "2026-08-01") == 14.78
    assert "2025-01-01" not in set(df.period)                         # malformed sheet skipped
    assert "2024-01-01" not in set(df.period)
    assert not df.duplicated(["series_id", "period"]).any()


def test_month_of():
    assert month_of("Aug-26") == "2026-08-01"
    assert month_of("Mar_26") == "2026-03-01"
    assert month_of("June 24") == "2024-06-01"
