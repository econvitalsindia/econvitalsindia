"""Release calendar: weekend shifts and series references."""
from datetime import date

from pipelines.build.calendar import load, shift
from pipelines.core import registry


def test_shift():
    sat = date(2026, 11, 28)
    assert shift(sat, "next_working_day") == date(2026, 11, 30)
    assert shift(sat, "previous_working_day") == date(2026, 11, 27)
    assert shift(sat, "none") == sat
    assert shift(date(2026, 11, 27), "next_working_day") == date(2026, 11, 27)


def test_calendar_files_load_and_reference_real_series():
    rows = load(set(registry.all_series()))
    assert rows and all(r["source_url"] for r in rows)
    assert all(date.fromisoformat(r["date"]).weekday() < 5 or r["publisher"] == "RBI" for r in rows)
