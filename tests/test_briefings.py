"""Briefing checker and ledger formatting."""
from pipelines.briefings.check import problems, render
from pipelines.briefings.ledger import data_decimals, fmt_period, fmt_value, phrase

FACTS = {"cpi_headline_inflation.latest": "5.54%", "const.rbi_inflation_target": "4%"}


def test_checker_blocks_typed_numbers_and_unknown_tokens():
    ok = "---\ntitle: x 2026\n---\nInflation was {{cpi_headline_inflation.latest}}; target {{const.rbi_inflation_target}}."
    assert problems(ok, FACTS) == []                       # digits in front matter are allowed
    typed = "---\n---\nInflation was 5.5% against {{cpi_headline_inflation.latest}}."
    assert any("typed outside a token" in p for p in problems(typed, FACTS))
    unknown = "---\n---\nCore was {{cpi_core_index:yoy.latest}}."
    assert any("not in ledger" in p for p in problems(unknown, FACTS))
    assert render("{{cpi_headline_inflation.latest}}", FACTS) == "5.54%"


def test_formatting():
    assert fmt_value(-30.21, "usd_bn", 1) == "−$30.2 billion"
    assert fmt_value(7.8, "percent", 1) == "7.8%"
    assert phrase(0.71, "percent", 2) == "up 0.71 percentage points"
    assert phrase(0.0, "percent", 2) == "unchanged"
    assert fmt_period("2026-04-01", "Q") == "Q1 FY27"
    assert fmt_period("2026-09-01", "M") == "September 2026"
    assert data_decimals([5.54, 4.83]) == 2 and data_decimals([7.8, 8.6]) == 1
