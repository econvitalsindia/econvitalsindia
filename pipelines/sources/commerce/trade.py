"""Merchandise trade, monthly, from the Department of Commerce's SDDS tables.

The ministry's site lists its monthly releases as JSON:
  https://www.commerce.gov.in/ministryofcommerce/api/v1/statistics-trade/current-figures-trade
Each "Merchandise Trade for SDDS" entry is a one-page PDF (files under
https://www.commerce.gov.in/files/...) with exports, imports and the balance in
US$ million for the month and the same month a year earlier. A later release
revises the year-earlier month, so the latest print wins: the list is newest first
and the first value seen for a month is kept. Values are stored in US$ billion.
"""
from __future__ import annotations

import io
import json
import re

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

LISTING = "https://www.commerce.gov.in/ministryofcommerce/api/v1/statistics-trade/current-figures-trade"
FILES = "https://www.commerce.gov.in"
ROWS = {"Total Exports": "merch_exports", "Total Imports": "merch_imports",
        "Trade Balance": "merch_trade_balance"}
MONTHS = ("January February March April May June July August September October "
          "November December").split()
NUM = r"(-?[\d,]+\.?\d*)"


def flexible(label: str) -> str:
    """Regex for `label` with optional whitespace between words (older PDFs drop spaces)."""
    return r"\s*".join(re.escape(w) for w in label.split())


def parse_sdds(text: str) -> list[dict]:
    """Rows for the reported month (provisional) and the same month a year earlier (revised).

    Layouts vary between releases: spaces may be missing ("TotalExports", "May2025") and
    the unit may wrap onto its own line, so labels match flexibly and the first two
    decimal numbers after each label are the month and the year-earlier values.
    """
    m = re.search(r"(" + "|".join(MONTHS) + r")\s*(\d{4})", text)
    if not m:
        raise ValueError("no 'Month YYYY' heading in SDDS table")
    month, year = MONTHS.index(m.group(1)) + 1, int(m.group(2))
    current, year_ago = f"{year:04d}-{month:02d}-01", f"{year - 1:04d}-{month:02d}-01"
    rows = []
    for label, sid in ROWS.items():
        r = re.search(flexible(label) + r"(.*)", text, re.S)
        nums = re.findall(r"-?\d[\d,]*\.\d+", r.group(1)) if r else []
        if len(nums) < 2:
            raise ValueError(f"row {label!r} not found in SDDS table")
        now, before = (float(x.replace(",", "")) / 1000 for x in nums[:2])
        rows += [{"series_id": sid, "period": current, "value": round(now, 3), "note": "provisional"},
                 {"series_id": sid, "period": year_ago, "value": round(before, 3), "note": "revised"}]
    return rows


class CommerceTrade(Source):
    name = "commerce_trade"
    series_ids = tuple(ROWS.values())

    def fetch(self) -> list[Raw]:
        listing = fetch_raw(LISTING)
        items = [i for i in json.loads(listing.content) if "SDDS" in i["title"]
                 and "Calendar" not in i["title"] and i.get("field_upload_pdf")]
        if not items:
            raise RuntimeError("no SDDS entries in the trade listing")
        return [listing] + [fetch_raw(FILES + i["field_upload_pdf"], suffix=".pdf") for i in items]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            if raw.suffix != ".pdf":
                continue
            with pdfplumber.open(io.BytesIO(raw.content)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            rows += parse_sdds(text)
        df = pd.DataFrame(rows)
        # Newest release first: keep its value for any month printed more than once.
        return df.drop_duplicates(subset=["series_id", "period"], keep="first")


SOURCE = CommerceTrade()
