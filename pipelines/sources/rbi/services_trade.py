"""India's international trade in services, monthly (RBI press release).

Listing: https://rbi.org.in/Scripts/Pr_DataRelease.aspx?SectionID=352 links each month's
"Monthly Data on India's International Trade in Services" press release (prid=...). Each
release tabulates every month of the financial year so far: receipts (exports) and
payments (imports) in US$ million, with y/y growth in brackets. Earlier months are
revised with balance-of-payments data, so the newest release wins. Stored in US$ bn.

These are RBI's actual data. The Commerce Ministry's monthly release projects the
latest month instead; we do not use that projection.
"""
from __future__ import annotations

import html
import re

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

LISTING = "https://rbi.org.in/Scripts/Pr_DataRelease.aspx?SectionID=352"
RELEASE = "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid={prid}"
MAX_RELEASES = 12
MONTHS = ("January February March April May June July August September October "
          "November December").split()
NUM = r"(-?[\d,]+(?:\.\d+)?)"
ROW = re.compile(r"(" + "|".join(MONTHS) + r")\s*[–-]\s*(\d{4})\s*\|\s*" + NUM + r"\s*\|\s*\((" + NUM[1:-1] + r")\)\s*\|\s*"
                 + NUM + r"\s*\|\s*\((" + NUM[1:-1] + r")\)")


def page_text(content: bytes) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content.decode("utf-8", errors="ignore"), flags=re.S)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " | ", t)))
    return re.sub(r"(\|\s*)+", "| ", t)


def number(s: str) -> float:
    return float(s.replace(",", ""))


def parse_release(text: str) -> list[dict]:
    rows = []
    for m in ROW.finditer(text):
        period = f"{int(m.group(2)):04d}-{MONTHS.index(m.group(1)) + 1:02d}-01"
        rows += [{"series_id": "services_exports", "period": period, "value": round(number(m.group(3)) / 1000, 3)},
                 {"series_id": "services_exports_growth", "period": period, "value": number(m.group(4))},
                 {"series_id": "services_imports", "period": period, "value": round(number(m.group(5)) / 1000, 3)},
                 {"series_id": "services_imports_growth", "period": period, "value": number(m.group(6))}]
    return rows


class RbiServicesTrade(Source):
    name = "rbi_services_trade"
    series_ids = ("services_exports", "services_imports", "services_exports_growth",
                  "services_imports_growth")

    def fetch(self) -> list[Raw]:
        listing = fetch_raw(LISTING, suffix=".html")
        prids = list(dict.fromkeys(re.findall(r"prid=(\d+)", listing.content.decode("utf-8", errors="ignore"))))
        if not prids:
            raise RuntimeError("no releases on the services trade listing page")
        return [fetch_raw(RELEASE.format(prid=p), suffix=".html") for p in prids[:MAX_RELEASES]]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:  # newest release first
            rows += parse_release(page_text(raw.content))
        df = pd.DataFrame(rows)
        if df.empty:
            raise ValueError("no month rows parsed from services trade releases")
        df["note"] = "RBI; latest release (earlier months revised with BoP data)"
        return df.drop_duplicates(subset=["series_id", "period"], keep="first")


SOURCE = RbiServicesTrade()
