"""Release calendar: registry/calendar/*.yaml -> calendar rows for the site and an .ics feed.

Weekend dates move by each file's holiday_rule. Public holidays are not known here,
so the guidebook runbook has a monthly check against the official calendars.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CAL_DIR = ROOT / "registry" / "calendar"


def shift(d: date, rule: str) -> date:
    """Move a Saturday/Sunday date to the next or previous working day."""
    step = {"next_working_day": 1, "previous_working_day": -1}.get(rule)
    while step and d.weekday() >= 5:
        d += timedelta(days=step)
    return d


def load(known_series: set[str]) -> list[dict]:
    rows = []
    for f in sorted(CAL_DIR.glob("*.yaml")):
        cal = yaml.safe_load(f.read_text())
        for r in cal["releases"]:
            scheduled = r["date"] if isinstance(r["date"], date) else date.fromisoformat(str(r["date"]))
            actual = shift(scheduled, cal.get("holiday_rule", "none"))
            unknown = set(r.get("series", [])) - known_series
            if unknown:
                raise ValueError(f"{f.name}: unknown series {sorted(unknown)}")
            rows.append({
                "date": actual.isoformat(), "scheduled": scheduled.isoformat(),
                "adjusted": actual != scheduled, "publisher": cal["publisher"],
                "title": r["title"], "period": r["period"], "series": r.get("series", []),
                "show": r.get("show", "level"),
                "time_ist": r.get("time_ist", cal.get("time_ist")),
                "estimated": bool(r.get("estimated")), "highlight": bool(r.get("highlight")),
                "source_url": r.get("source_url", cal["source_url"]),
            })
    return sorted(rows, key=lambda r: (r["date"], r["publisher"]))


def ics(rows: list[dict], site_name: str) -> str:
    """All-day VEVENTs (times vary and are often unannounced)."""
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{site_name}//release calendar//EN",
             f"X-WR-CALNAME:{site_name}: Indian data releases"]
    for i, r in enumerate(rows):
        d = r["date"].replace("-", "")
        end = (date.fromisoformat(r["date"]) + timedelta(days=1)).isoformat().replace("-", "")
        desc = f"{r['publisher']}, {r['period']}" + (" (date estimated)" if r["estimated"] else "")
        lines += ["BEGIN:VEVENT", f"UID:{d}-{i}@release-calendar", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{d}", f"DTEND;VALUE=DATE:{end}",
                  f"SUMMARY:{r['title']} ({r['period']})", f"DESCRIPTION:{desc}",
                  f"URL:{r['source_url']}", "END:VEVENT"]
    return "\r\n".join(lines + ["END:VCALENDAR"]) + "\r\n"
