"""MoSPI CPI parser. Pinned values are as published by MoSPI's API; the
Oct 2024 (6.21%) and Dec 2025 (1.33%) headline rates match the press releases."""
from pipelines.sources.mospi.cpi import SOURCE, months_since


def value(df, sid, period):
    row = df[(df.series_id == sid) & (df.period == period)]
    assert len(row) == 1, (sid, period, len(row))
    return row.iloc[0]


def test_parse_current_back_and_2012(raw_from):
    raws = [raw_from(f"mospi/cpi/{f}.json") for f in ("b2024_back", "b2024_current", "b2012")]
    df = SOURCE.parse(raws)
    assert value(df, "cpi_headline_index", "2026-09-01").value == 109.49
    assert value(df, "cpi_rural_index", "2026-09-01").value == 110.11
    assert value(df, "cpi_urban_index", "2026-09-01").value == 108.71
    assert value(df, "cpi_food_bev_index", "2026-09-01").value == 111.77
    assert value(df, "cpi_headline_index", "2024-12-01").value == 102.90   # back series
    # Published inflation: 2024-base where available, 2012-base for 2025.
    assert value(df, "cpi_headline_inflation", "2026-09-01").value == 5.54
    assert value(df, "cpi_headline_inflation", "2024-12-01").value == 5.22
    dec25 = value(df, "cpi_headline_inflation", "2025-12-01")
    assert dec25.value == 1.33 and "2012" in dec25.note


def test_no_duplicate_periods(raw_from):
    raws = [raw_from(f"mospi/cpi/{f}.json") for f in ("b2024_back", "b2024_current", "b2012")]
    df = SOURCE.parse(raws)
    assert not df.duplicated(["series_id", "period"]).any()


def test_months_since_crosses_year():
    out = months_since("2026-01-01", back=2)
    assert out[2025] == [11, 12] and out[2026][0] == 1
    assert months_since(float("nan"), back=2) is None
