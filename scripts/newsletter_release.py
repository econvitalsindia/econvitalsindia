"""Release a sign-up held by Buttondown's spam filter: set it to "unactivated", which makes
Buttondown send a fresh confirmation email (the reader is subscribed once they click it).

    BUTTONDOWN_API_KEY=... uv run python scripts/newsletter_release.py someone@example.com

Run by .github/workflows/newsletter-release.yml. Prints the result with the address masked.
"""
from __future__ import annotations

import os
import sys

import httpx

from scripts.newsletter_status import API, mask


def main() -> int:
    email = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not (email and key):
        print("usage: needs an email argument and BUTTONDOWN_API_KEY")
        return 1
    h = {"Authorization": f"Token {key}"}
    with httpx.Client(headers=h, timeout=60) as c:
        r = c.get(f"{API}/subscribers/{email}")
        before = r.json().get("type") if r.status_code == 200 else f"HTTP {r.status_code}"
        r = c.patch(f"{API}/subscribers/{email}", json={"type": "unactivated"})
        after = r.json().get("type") if r.status_code == 200 else f"HTTP {r.status_code}: {r.text[:300]}"
    print(f"{mask(email)}: {before} -> {after}")
    return 0 if r.status_code == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
