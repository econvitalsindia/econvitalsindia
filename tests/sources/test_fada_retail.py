"""FADA vehicle retail parser, pinned to the July 2025 and September 2026 releases."""
from pipelines.sources.fada.retail import SOURCE, parse_release


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_release_table(raw_from):
    rows = parse_release(raw_from("fada/2026-09.pdf").content)
    got = {(r["series_id"], r["period"]): r["value"] for r in rows}
    assert got[("vehicle_retail_total", "2026-09-01")] == 2536.92            # thousand units
    assert got[("vehicle_retail_2w", "2025-09-01")] == 1345.153              # year-ago column
    assert got[("vehicle_retail_tractor_growth", "2026-09-01")] == 13.75
    assert ("vehicle_retail_cv", "2026-08-01") in got                       # previous-month column


def test_full_month_names_and_newest_wins(raw_from):
    # "July'25" headers; the Sep 2026 release restates Sep 2025 (1,924,546 vs its own 1,827,340).
    df = SOURCE.parse([raw_from("fada/2025-07.pdf"), raw_from("fada/2026-09.pdf")])
    assert at(df, "vehicle_retail_total", "2025-07-01") == 1964.213
    assert at(df, "vehicle_retail_total_growth", "2025-07-01") == -4.31
    assert at(df, "vehicle_retail_total", "2025-09-01") == 1924.546
    assert not df.duplicated(["series_id", "period"]).any()
