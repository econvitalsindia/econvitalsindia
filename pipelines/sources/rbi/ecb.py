"""External commercial borrowing registered each month, from RBI's ECB data pages.

RBI's monthly release "RBI releases data on ECB / FCCB / RDB for <Month> <YYYY>" links a page
https://www.rbi.org.in/Scripts/ECBUserView.aspx?Id=<n> (n rises by one a month) listing every
ECB/FCCB that received a loan registration number in the month, in US dollars, then a grand
total: "Total(General + Special)" on recent pages, "Total(Automatic+Approval)" or
"Total(Auto+Approval)" earlier, a bare "Total" in 2024 (the routes were renamed). Amounts use Indian digit grouping (8,12,88,76,672.44). The month comes
from "Data on ECB/FCCB for the Month of August 2026".

Series: ecb_registrations (US$ billion a month). Registrations are plans, not money received.
"""
from __future__ import annotations

import html
import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series
from pipelines.sources.rbi._press import RELEASE, releases

PAGE = "https://www.rbi.org.in/Scripts/ECBUserView.aspx?Id={id}"
BACKFILL, RECENT, MIN_HISTORY = 30, 3, 12
MONTH = re.compile(r"Data on ECB/\s*FCCB\s+for the month of\s+([A-Z][a-z]+)\s+(\d{4})", re.I)
# The grand total: "Total(General + Special)", "Total(Automatic+Approval)", "Total(Auto+Approval)";
# 2024 pages print a bare "Total 4,01,20,56,378" after the two route totals.
TOTAL = re.compile(r"Total\s*\(\s*[A-Za-z]+\s*\+\s*[A-Za-z]+\s*\)\s*([\d,]+(?:\.\d+)?)")
BARE_TOTAL = re.compile(r"\bTotal\s+([\d,]+(?:\.\d+)?)")


def text_of(content: bytes) -> str:
    raw = content.decode("utf-8", "ignore")
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S))).split())


def parse_page(content: bytes) -> dict | None:
    t = text_of(content)
    month, total = MONTH.search(t), TOTAL.search(t) or BARE_TOTAL.search(t)
    if not (month and total):
        return None
    period = datetime.strptime(f"{month.group(1)[:3]} {month.group(2)}", "%b %Y").strftime("%Y-%m-01")
    return {"series_id": "ecb_registrations", "period": period,
            "value": round(float(total.group(1).replace(",", "")) / 1e9, 3)}


def latest_id() -> int:
    found = releases(lambda t: t.startswith("RBI releases data on ECB"), 3)
    for prid in sorted(found, reverse=True):
        m = re.search(r"ECBUserView\.aspx\?Id=(\d+)", get(RELEASE.format(prid=prid)).text)
        if m:
            return int(m.group(1))
    raise RuntimeError("no ECB data page linked from recent releases")


class RbiECB(Source):
    name = "rbi_ecb"
    series_ids = ("ecb_registrations",)

    def fetch(self) -> list[Raw]:
        top = latest_id()
        n = BACKFILL if len(load_series("ecb_registrations")) < MIN_HISTORY else RECENT
        return [fetch_raw(PAGE.format(id=i), suffix=".html") for i in range(top - n + 1, top + 1)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = [r for r in (parse_page(raw.content) for raw in raws) if r]
        if not rows:
            raise ValueError("no ECB totals found")
        out = pd.DataFrame(rows).drop_duplicates(["period"], keep="last")
        out["note"] = "registrations (loan registration numbers allotted), RBI"
        return out


SOURCE = RbiECB()
