"""BIS effective exchange rates, RBI external debt, and remittances from the BoP release."""
from pipelines.sources.bis.eer import SOURCE as BIS
from pipelines.sources.rbi.bop import fy_quarter_start, parse_quarterly
from pipelines.sources.rbi.external_debt import SOURCE as DEBT
from pipelines.sources.rbi.services_trade import page_text


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_bis_eer(raw_from):
    df = BIS.parse([raw_from("bis/eer_india.csv")])
    assert at(df, "reer_bis_broad", "2026-09-01") == 90.17
    assert at(df, "neer_bis_broad", "2026-09-01") == 80.48


def test_external_debt(raw_from):
    # Oldest first; "recording an increase" (2023) and "an increase" (2026) wordings.
    df = DEBT.parse([raw_from("rbi/external_debt_2023-06.html"), raw_from("rbi/external_debt_2026-06.html")])
    assert at(df, "external_debt", "2026-04-01") == 778.2          # end-June 2026
    assert at(df, "external_debt", "2026-01-01") == 762.8          # 778.2 - 15.4, end-March 2026
    assert at(df, "external_debt", "2023-04-01") == 629.1
    assert at(df, "external_debt_pct_gdp", "2026-04-01") == 20.8
    assert at(df, "external_debt_pct_gdp", "2023-01-01") == 18.8


def test_remittances_from_bop_text(raw_from):
    rows = parse_quarterly(page_text(raw_from("rbi/bop/q1_2026-27.html").content))
    got = {r["period"]: r["value"] for r in rows if r["series_id"] == "bop_remittances"}
    assert got == {"2026-04-01": 42.9, "2025-04-01": 33.2}


def test_fy_quarter_start():
    assert fy_quarter_start(1, 2026) == "2026-04-01"
    assert fy_quarter_start(4, 2025) == "2026-01-01"
