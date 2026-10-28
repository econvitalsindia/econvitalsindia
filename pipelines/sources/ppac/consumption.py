"""Domestic consumption of petroleum products, monthly, PPAC (Ministry of Petroleum).

The products-wise page (https://ppac.gov.in/consumption/products-wise) loads its table by
POSTing to /AjaxController/getConsumptionPetroleumProductsData with
financialYear=<YYYY-YYYY>&reportBy=1&pageId=43 (an XHR from that page). Each financial year
returns one row per product with April...March in '000 tonnes. Data are provisional and
revised; the newest pull wins.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone

import httpx
import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import HEADERS
from pipelines.core.store import load_series

PAGE = "https://ppac.gov.in/consumption/products-wise"
AJAX = "https://ppac.gov.in/AjaxController/getConsumptionPetroleumProductsData"
FIRST_FY = 2023
PRODUCTS = {"TOTAL": "fuel_consumption_total", "HSD": "diesel_consumption", "MS": "petrol_consumption",
            "ATF": "atf_consumption", "LPG": "lpg_consumption"}
MONTHS = ["april", "may", "june", "july", "august", "september", "october", "november",
          "december", "january", "february", "march"]


def fy_label(start: int) -> str:
    return f"{start}-{start + 1}"


class PpacConsumption(Source):
    name = "ppac_consumption"
    series_ids = tuple(PRODUCTS.values())

    def fetch(self) -> list[Raw]:
        today = date.today()
        current = today.year if today.month >= 4 else today.year - 1
        backfill = len(load_series("fuel_consumption_total")) < 24
        years = range(FIRST_FY if backfill else current - 1, current + 1)
        raws = []
        with httpx.Client(headers=HEADERS, timeout=60, follow_redirects=True) as client:
            client.get(PAGE)
            for start in years:
                r = client.post(AJAX, data={"financialYear": fy_label(start), "reportBy": 1, "pageId": 43},
                                headers={"X-Requested-With": "XMLHttpRequest", "Referer": PAGE})
                r.raise_for_status()
                body = json.dumps({"fy_start": start, "data": r.json()}).encode()
                raws.append(Raw(body, f"{AJAX}?financialYear={fy_label(start)}", datetime.now(timezone.utc),
                                hashlib.sha256(body).hexdigest(), ".json"))
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            body = json.loads(raw.content)
            start = body["fy_start"]
            result = body["data"].get("result") or {}
            if not result:
                raise ValueError(f"PPAC returned no rows for FY starting {start}")
            for item in result.values():
                title = re.sub(r"<[^>]+>", "", str(item.get("title", ""))).strip()
                sid = PRODUCTS.get(title)
                if not sid:
                    continue
                for i, m in enumerate(MONTHS):
                    v = item.get(m)
                    if v in ("", None):
                        continue
                    year = start if i < 9 else start + 1
                    rows.append({"series_id": sid, "period": f"{year}-{(i + 3) % 12 + 1:02d}-01",
                                 "value": float(v), "note": "provisional (PPAC)"})
        return pd.DataFrame(rows)


SOURCE = PpacConsumption()
