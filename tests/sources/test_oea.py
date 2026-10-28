"""OEA WPI and core-industries parsers, pinned to the October 2026 download files.
WPI Sep-26 y/y (11.39%) matches OEA's press release; core growth matches OEA's sheet."""
from pipelines.sources.oea._site import month_label
from pipelines.sources.oea.core8 import SOURCE as CORE
from pipelines.sources.oea.wpi import SOURCE as WPI


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_wpi(raw_from):
    df = WPI.parse([raw_from("oea/wpi/2026-10.xlsx")])
    assert at(df, "wpi_headline_index", "2026-09-01") == 112.5
    assert at(df, "wpi_manufactured_index", "2026-09-01") == 110.2
    yoy = (at(df, "wpi_headline_index", "2026-09-01") / at(df, "wpi_headline_index", "2025-09-01") - 1) * 100
    assert round(yoy, 2) == 11.39


def test_core_industries(raw_from):
    df = CORE.parse([raw_from("oea/core8/2026-10.xlsx")])
    assert at(df, "core_overall_index", "2026-09-01") == 118.3
    assert at(df, "core_iron_ore_index", "2026-09-01") == 108.3
    assert df.period.min() == "2023-04-01"  # annual rows skipped


def test_month_label():
    assert month_label("Sep-26") == "2026-09-01"
    assert month_label("2025-26(Apr-Mar)") is None
