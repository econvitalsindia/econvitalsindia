"""FBIL reference rate history (INR per USD), last 12 months.

Endpoint used by fbil.org.in's own chart: /wasdm/refrates/fetchcommongraph/12M
(12M is the longest window offered). The free public view appears to lag about a
week behind publication, so this source backfills history; the same-day value
comes from the RBI home page (pipelines/sources/rbi/home_rates.py). Both write
`usdinr_ref`; values agree because RBI republishes the FBIL rate.
"""
from __future__ import annotations

import json

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://www.fbil.org.in/wasdm/refrates/fetchcommongraph/12M"
PRODUCTS = {"Reference Rate - INR / 1 USD": "usdinr_ref"}


class FbilRefRates(Source):
    name = "fbil_refrates"
    series_ids = tuple(PRODUCTS.values())

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for product in json.loads(raws[0].content)["benchMarkTrendData"]:
            sid = PRODUCTS.get(product["productName"])
            if sid:
                rows += [{"series_id": sid, "period": p["publishDate"], "value": float(p["rate"]),
                          "note": "FBIL reference rate"} for p in product["benchMarkTrend"]]
        return pd.DataFrame(rows)


SOURCE = FbilRefRates()
