"""Brent crude in rupees per barrel: Brent (US$, front-month future) x USD/INR reference rate.

Each Brent close is converted at the FBIL reference rate on the same date, or the
latest earlier one if none was set that day (Mumbai holidays). Original measure.
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_series


class BrentInr(Source):
    name = "derived_brent_inr"
    derived = True
    series_ids = ("brent_inr",)

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        brent = load_series("brent_usd")[["period", "value"]].astype({"value": float})
        fx = load_series("usdinr_ref")[["period", "value"]].astype({"value": float})
        brent["date"], fx["date"] = pd.to_datetime(brent["period"]), pd.to_datetime(fx["period"])
        m = pd.merge_asof(brent.sort_values("date"), fx.sort_values("date")[["date", "value"]],
                          on="date", suffixes=("_usd", "_fx"), tolerance=pd.Timedelta(days=5))
        m = m.dropna(subset=["value_fx"])
        return pd.DataFrame({"series_id": "brent_inr", "period": m["period"],
                             "value": (m["value_usd"] * m["value_fx"]).round(2),
                             "note": "site calculation: Brent (US$) x FBIL USD/INR"})


SOURCE = BrentInr()
