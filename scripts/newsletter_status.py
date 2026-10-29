"""Newsletter status from Buttondown: the newsletter's name and each subscriber, masked.

    BUTTONDOWN_API_KEY=... uv run python scripts/newsletter_status.py

Prints counts by subscriber type (e.g. regular = confirmed, unactivated = has not clicked the
confirmation link) and each address masked as b***@gmail.com with its type and sign-up time,
so the output can sit in a public log. Run by .github/workflows/newsletter-status.yml.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

import httpx

API = "https://api.buttondown.com/v1"


def mask(email: str) -> str:
    user, _, domain = email.partition("@")
    return f"{user[:1]}***@{domain}"


def main() -> int:
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not key:
        print("BUTTONDOWN_API_KEY not set")
        return 1
    h = {"Authorization": f"Token {key}"}
    with httpx.Client(headers=h, timeout=60) as c:
        r = c.get(f"{API}/newsletters")
        if r.status_code == 200:
            for n in r.json().get("results", []):
                print(f"newsletter: name={n.get('name')!r} username={n.get('username')!r}")
        else:
            print(f"newsletters: HTTP {r.status_code} {r.text[:200]}")
        subs, url = [], f"{API}/subscribers?page_size=100"
        while url:
            r = c.get(url)
            if r.status_code != 200:
                print(f"subscribers: HTTP {r.status_code} {r.text[:300]}")
                return 1
            body = r.json()
            subs += body.get("results", [])
            url = body.get("next")
        types = Counter(s.get("type") or s.get("subscriber_type") for s in subs)
        print(f"subscribers: {len(subs)} total; by type: {dict(types)}")
        for s in sorted(subs, key=lambda s: s.get("creation_date", "")):
            print(f"  {mask(s.get('email_address') or s.get('email', '?'))}  type={s.get('type') or s.get('subscriber_type')}"
                  f"  created={s.get('creation_date', '')[:19]}  source={s.get('source', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
