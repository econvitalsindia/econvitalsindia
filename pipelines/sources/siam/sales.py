"""Domestic vehicle sales (dispatches by manufacturers), monthly, SIAM press releases.

SIAM (Society of Indian Automobile Manufacturers, an industry body) posts a release around
the 12th-15th of each month at https://www.siam.in/news-&-updates/press-releases/<slug>/<id>.
The slug is ignored, so releases can be walked by id. Each has a "Domestic Sales" paragraph:
"Passenger Vehicles 2 sales were 4,39,309 units in August 2026. Three-wheeler sales were ...".
Quarter-end releases repeat the sentence for the quarter and the year to date
("in July-September 2026"); those are skipped because no single month follows "in".

Coverage: BMW, Mercedes, JLR and Volvo Auto never report. Tata Motors' passenger vehicles
are included only from April 2023, so passenger vehicles start there (a consistent
universe); two- and three-wheelers start in April 2021 (release id 482).
"""
from __future__ import annotations

import html
import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series

LIST = "https://www.siam.in/news-&-updates/press-releases"
PAGE = "https://www.siam.in/news-&-updates/press-releases/x/{id}"
FIRST_ID = 482
PV_FROM = "2023-04-01"
SERIES = {"pas": "auto_pv_sales", "two": "auto_2w_sales", "thr": "auto_3w_sales"}   # by first three letters
SALES = re.compile(
    r"(Passenger Vehicles?|Three[- ]?wheelers?|Two[- ]?wheelers?)\s*[\d*#]*\s*(?:domestic\s+)?sales\s+"
    r"(?:were|was)\s+(?:units\s+)?([\d,]+)\s*units\s+in\s+(?:the month of\s+)?([A-Z][a-z]+)[\s-]*(\d{4})"
    r"(?!\s*(?:to\b|[-–]))", re.I)


def text_of(content: bytes) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", content.decode("utf-8", "ignore"))))


def title_of(text: str) -> str:
    k = text.find("Press Releases Back")
    return text[k + 21:k + 160] if k >= 0 else ""


def is_sales_release(text: str) -> bool:
    return bool(re.match(r"\s*Auto Industry (?:Sales )?Performance", title_of(text), re.I))


def parse_release(text: str) -> list[dict]:
    rows = {}
    for kind, units, month, year in SALES.findall(text):
        sid = SERIES[kind.lower()[:3]]
        period = datetime.strptime(f"{month[:3]} {year}", "%b %Y").strftime("%Y-%m-01")
        if sid == "auto_pv_sales" and period < PV_FROM:
            continue
        rows.setdefault((sid, period), float(units.replace(",", "")))
    return [{"series_id": s, "period": p, "value": v, "note": "SIAM press release"} for (s, p), v in rows.items()]


class SiamSales(Source):
    name = "siam_sales"
    series_ids = tuple(SERIES.values())

    def fetch(self) -> list[Raw]:
        listing = get(LIST).text
        ids = sorted({int(i) for i in re.findall(r'press-releases/[^"/]*perform[^"/]*/(\d+)"', listing, re.I)})
        if not ids:
            raise ValueError("no 'performance' releases on the SIAM press list; the page layout may have changed")
        if len(load_series("auto_2w_sales")) < 24:
            ids = range(FIRST_ID, max(ids) + 1)
        return [fetch_raw(PAGE.format(id=i), suffix=".html") for i in ids]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            text = text_of(raw.content)
            if is_sales_release(text):
                rows += parse_release(text)
        return pd.DataFrame(rows)


SOURCE = SiamSales()
