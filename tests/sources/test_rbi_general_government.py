"""Combined Centre + states deficits and debt (RBI Handbook tables 239, 240)."""
from pipelines.sources.rbi.general_government import parse_table


def test_deficits_and_stage(raw_from):
    rows = {(r["series_id"], r["period"]): r for r in parse_table(raw_from("rbi/handbook/hbie239.xlsx").content, 239)}
    assert rows[("gg_gfd_pct_gdp", "2020-04-01")]["value"] == 13.1
    assert rows[("gg_gfd_pct_gdp", "2025-04-01")]["note"] == "Budget Estimates"
    assert rows[("gg_revenue_deficit_pct_gdp", "2024-04-01")]["note"] == "Revised Estimates"


def test_debt_columns(raw_from):
    rows = {(r["series_id"], r["period"]): r["value"] for r in parse_table(raw_from("rbi/handbook/hbie240.xlsx").content, 240)}
    assert rows[("gg_debt_pct_gdp", "2025-04-01")] == 81.85
    assert rows[("centre_debt_pct_gdp", "2025-04-01")] == 56.17
    assert rows[("states_debt_pct_gdp", "1985-04-01")] == 21.19
