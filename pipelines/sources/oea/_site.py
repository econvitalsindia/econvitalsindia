"""Helpers for eaindustry.nic.in (Office of the Economic Adviser, DPIIT).

Download files carry their update date in the name (wpi_monthly_index_202610.xlsx), so
each run reads the download page and takes the current link. The server omits its
intermediate certificate; pipelines/core/http.py handles that (INCOMPLETE_CHAIN_HOSTS).
"""
from __future__ import annotations

import re
from datetime import datetime

from pipelines.core.http import get

BASE = "https://eaindustry.nic.in/"


def find_link(page: str, pattern: str) -> str:
    """Absolute URL of the first href on `page` matching the regex `pattern`."""
    html = get(BASE + page).text
    m = re.search(r'href="(' + pattern + r')"', html)
    if not m:
        raise RuntimeError(f"no link matching {pattern!r} on {BASE + page} (page layout changed?)")
    return BASE + m.group(1).replace(" ", "%20")


def month_label(label: str) -> str | None:
    """"Sep-26" -> "2026-09-01"; None for anything else (e.g. annual rows)."""
    try:
        return datetime.strptime(str(label).strip(), "%b-%y").strftime("%Y-%m-01")
    except ValueError:
        return None
