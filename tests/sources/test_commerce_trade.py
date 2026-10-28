"""Commerce SDDS trade tables in both layouts (with and without spaces)."""
from pipelines.sources.commerce.trade import SOURCE


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_sdds_layouts(raw_from):
    df = SOURCE.parse([raw_from("commerce/sdds/2026-09.pdf"), raw_from("commerce/sdds/2025-05-nospaces.pdf")])
    assert at(df, "merch_exports", "2026-09-01") == 44.4          # US$ bn (44,400.33 mn)
    assert at(df, "merch_imports", "2026-09-01") == 74.61
    assert at(df, "merch_trade_balance", "2026-09-01") == -30.21
    assert at(df, "merch_exports", "2025-09-01") == 36.085        # year-earlier column
    assert at(df, "merch_exports", "2025-05-01") == 38.73         # no-spaces layout
    assert at(df, "merch_trade_balance", "2024-05-01") == -22.084
