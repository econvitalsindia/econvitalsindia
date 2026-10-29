"""Sectoral deployment of bank credit: published y/y growth, two months per release."""
from pipelines.sources.rbi.sectoral_credit import ROWS, parse_statement


def test_sectoral_credit(raw_from):
    rows = parse_statement(raw_from("rbi/sibc_2026-08.xlsx").content)
    got = {(r["series_id"], r["period"]): r["value"] for r in rows}
    assert got[("credit_agri_growth", "2026-08-01")] == 17.22
    assert got[("credit_agri_growth", "2025-08-01")] == 7.59        # year-earlier column
    assert got[("credit_gold_growth", "2026-08-01")] == 83.23
    # Bank credit's year-earlier date is a September Friday; it still belongs to August.
    assert got[("credit_nonfood_growth", "2025-08-01")] == 10.16
    assert {s for s, _ in got} == set(ROWS.values())
