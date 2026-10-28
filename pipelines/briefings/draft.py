"""Draft release notes from templates for releases that arrived on a given day.

    python -m pipelines.briefings.draft                  # releases first recorded today
    python -m pipelines.briefings.draft --date 2026-10-28
    python -m pipelines.briefings.draft --force cpi       # draft one template regardless
    python -m pipelines.briefings.draft --check-only      # validate every template

A template (registry/briefings/<name>.md) is drafted when its trigger series has an
observation first recorded (vintage) on the date. Each draft is checked
(pipelines/briefings/check.py), rendered to site/src/content/briefings/<date>-<name>.md,
and its ledger saved to data/briefings/<date>-<name>.json. The briefing workflow opens a
pull request with these files: merging it is the human approval that publishes the note
(07-editorial-policy.md). Nothing reaches main, and so the site, without that merge.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

import yaml

from pipelines.briefings.check import body_of, problems, render
from pipelines.briefings.ledger import Ledger
from pipelines.core import store

TEMPLATES = store.ROOT / "registry" / "briefings"
OUT = store.ROOT / "site" / "src" / "content" / "briefings"
LEDGERS = store.ROOT / "data" / "briefings"


def templates() -> dict[str, tuple[dict, str]]:
    out = {}
    for f in sorted(TEMPLATES.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text()
        front = yaml.safe_load(text.split("---")[1])
        out[front["name"]] = (front, text)
    return out


def build_ledger(front: dict, on: str | None = None) -> Ledger:
    ledger = Ledger()
    if front.get("calendar"):
        ledger.add_calendar(on or date.today().isoformat())
    for view in front["views"]:
        sid, _, how = view.partition(":")
        ledger.add_view(sid, how or "level")
    ledger.add_constants(TEMPLATES / "constants.yaml")
    return ledger


def triggered(front: dict, on: str) -> bool:
    """Should this template be drafted for date `on`?

    trigger_calendar: a calendar release whose title starts with this text is dated `on`
                      (e.g. MPC decisions: a hold deserves a note as much as a change).
    trigger:          the series' newest observation was first recorded on `on`;
                      with trigger_weekdays_only, only Monday-Friday.
    """
    if "trigger_calendar" in front:
        from pipelines.build import calendar as cal
        from pipelines.core.registry import all_series
        return any(r["date"] == on and r["title"].startswith(front["trigger_calendar"])
                   for r in cal.load(set(all_series())))
    if front.get("trigger_weekdays_only") and date.fromisoformat(on).weekday() >= 5:
        return False
    df = store.load_series(front["trigger"])
    if df.empty:
        return False
    return str(df.sort_values("period").iloc[-1]["vintage"]) == on


def draft(name: str, front: dict, text: str, on: str) -> tuple[str | None, list[str]]:
    ledger = build_ledger(front, on)
    issues = problems(text, ledger.facts) + problems("---\n---\n" + front["title"], ledger.facts)
    if issues:
        return None, issues
    slug = f"{on}-{name}"
    body = render(body_of(text).strip(), ledger.facts)
    title = render(front["title"], ledger.facts)
    OUT.mkdir(parents=True, exist_ok=True)
    LEDGERS.mkdir(parents=True, exist_ok=True)
    meta = {"title": title, "date": on, "product": front.get("product", "release-note"), "template": name,
            "drafted_by": "template (no AI)", "reviewed_via": "pull request merge", "ledger": f"data/briefings/{slug}.json"}
    (OUT / f"{slug}.md").write_text("---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
                                    + "---\n" + body + "\n")
    (LEDGERS / f"{slug}.json").write_text(ledger.dump())
    return slug, []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--force", nargs="*", default=[], help="template names to draft regardless of trigger")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    failed = 0
    for name, (front, text) in templates().items():
        if args.check_only:
            issues = problems(text, build_ledger(front).facts)
            print(f"{'FAIL' if issues else 'ok  '} {name}" + "".join(f"\n     {i}" for i in issues))
            failed += bool(issues)
            continue
        if name not in args.force and not triggered(front, args.date):
            continue
        slug, issues = draft(name, front, text, args.date)
        if issues:
            failed += 1
            print(f"FAIL {name}:" + "".join(f"\n     {i}" for i in issues))
        else:
            print(f"drafted {slug}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
