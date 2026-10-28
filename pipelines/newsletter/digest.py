"""Weekly newsletter digest from published briefings, sent to the provider as a DRAFT.

    python -m pipelines.newsletter.digest                 # digest for the week to today
    python -m pipelines.newsletter.digest --date 2026-10-31
    python -m pipelines.newsletter.digest --preview out.md  # write the email, contact nobody

The digest is the latest weekly briefing of the seven days to the date (if any) followed by
links to the other briefings of the included products (site.config.yaml newsletter.products) published
in the seven days to the date. Only briefings already on main are used, so everything in
the email has been through the briefing review (07-editorial-policy.md).

With BUTTONDOWN_API_KEY set and newsletter.enabled true, it creates a draft with Buttondown
(POST /v1/emails, status "draft"); a person reviews and sends it from the dashboard. Nothing
is ever sent from here. data/newsletter/drafted.json records which dates were drafted, so a
rerun does not create a duplicate.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta

import httpx
import yaml

from pipelines.briefings.check import body_of
from pipelines.core.store import ROOT

BRIEFINGS = ROOT / "site" / "src" / "content" / "briefings"
STATE = ROOT / "data" / "newsletter" / "drafted.json"
API = "https://api.buttondown.com/v1/emails"


def config() -> dict:
    return yaml.safe_load((ROOT / "site.config.yaml").read_text())


def published(products: list[str], start: date, end: date) -> list[dict]:
    out = []
    for f in sorted(BRIEFINGS.glob("*.md")):
        text = f.read_text()
        meta = yaml.safe_load(text.split("---")[1])
        when = date.fromisoformat(str(meta["date"]))
        if start <= when <= end and meta.get("product", "release-note") in products:
            out.append({**meta, "slug": f.stem, "body": body_of(text).strip()})
    return out


def compose(on: date, cfg: dict) -> tuple[str, str] | None:
    """(subject, markdown body), or None when there is nothing to send."""
    site = cfg["site"]
    items = published(cfg["newsletter"]["products"], on - timedelta(days=6), on)
    if not items:
        return None
    link = lambda b: f"{site['url']}/briefings/{b['slug']}/"
    weekly = next((b for b in reversed(items) if b.get("product") == "weekly-briefing"), None)
    others = [b for b in items if b is not weekly]
    parts = []
    if weekly:
        parts += [weekly["body"], f"[Read on the site]({link(weekly)})"]
    if others:
        parts += ["## Notes this week" if weekly else "## This week's notes",
                  "\n".join(f"- [{b['title']}]({link(b)}) ({b['date']})" for b in others)]
    parts += ["---", f"{site['name']}: {site['tagline']}. Every number comes from official public "
              f"sources; see {site['url']}/data/. {' '.join(cfg['credit']['inspired_by_text'].split())} "
              f"{cfg['credit']['inspired_by_url']}"]
    subject = weekly["title"] if weekly else f"{site['name']}: the week to {on.strftime('%-d %b %Y')}"
    return subject, "\n\n".join(parts) + "\n"


def drafted() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def create_draft(subject: str, body: str, key: str) -> str:
    r = httpx.post(API, headers={"Authorization": f"Token {key}"}, timeout=60,
                   json={"subject": subject, "body": body, "status": "draft"})
    r.raise_for_status()
    return r.json().get("id", "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--preview", help="write the email to this file instead of contacting the provider")
    args = ap.parse_args()
    on, cfg = date.fromisoformat(args.date), config()
    email = compose(on, cfg)
    if email is None:
        print(f"nothing published in the week to {on}; no digest")
        return 0
    subject, body = email
    if args.preview:
        open(args.preview, "w").write(f"Subject: {subject}\n\n{body}")
        print(f"preview written to {args.preview}")
        return 0
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not (cfg["newsletter"]["enabled"] and key):
        print("newsletter disabled or BUTTONDOWN_API_KEY not set; nothing created (use --preview to see the email)")
        return 0
    state = drafted()
    if on.isoformat() in state:
        print(f"digest for {on} already drafted ({state[on.isoformat()]}); skipping")
        return 0
    state[on.isoformat()] = create_draft(subject, body, key)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))
    print(f"draft created with Buttondown for {on}: {subject}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
