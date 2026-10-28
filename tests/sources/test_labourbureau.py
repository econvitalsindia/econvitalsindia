"""CPI-IW press note (August 2026)."""
from pipelines.sources.labourbureau.cpi_iw import SOURCE


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_cpi_iw(raw_from):
    df = SOURCE.parse([raw_from("labourbureau/cpi_iw_2026-08.pdf")])
    assert at(df, "cpi_iw_index", "2026-08-01") == 154.4
    assert at(df, "cpi_iw_index", "2026-07-01") == 153.2
    assert at(df, "cpi_iw_inflation", "2026-08-01") == 4.96
    assert at(df, "cpi_iw_inflation", "2025-08-01") == 3.16
