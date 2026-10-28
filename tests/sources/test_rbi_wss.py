"""RBI WSS parsers, pinned to the WSS published 23 Oct 2026."""
from pipelines.sources.rbi.wss import SOURCE, parse_date


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_wss(raw_from):
    raws = [raw_from(f"rbi/wss/2026-10-23.s{n}.xlsx") for n in (2, 3, 4)]
    df = SOURCE.parse(raws)
    assert at(df, "fx_reserves_total", "2026-10-16") == 721.016          # US$ bn
    assert at(df, "scb_credit", "2026-10-15") == 227.42777               # ₹ lakh crore
    assert at(df, "scb_credit_growth", "2026-10-15") == 18.2
    assert at(df, "repo_rate", "2026-10-16") == 5.5
    assert at(df, "repo_rate", "2026-09-18") == 5.25
    assert at(df, "wacr", "2026-10-16") == 5.56
    assert at(df, "gsec_10y_par_fbil", "2026-10-16") == 7.4
    assert at(df, "crr", "2025-10-17") == 3.5                            # year-earlier column
    assert not df.duplicated(["series_id", "period"]).any()


def test_parse_date():
    assert parse_date("As on October 16, 2026") == "2026-10-16"
    assert parse_date("Outstanding as on Oct. 15, 2026") == "2026-10-15"
    assert parse_date("Sep. 18", 2026) == "2026-09-18"
    assert parse_date("Sept. 18", 2026) == "2026-09-18"
