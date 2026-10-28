"""MoSPI Index of Industrial Production (base 2022-23), all-India, monthly.

API: GET https://api.mospi.gov.in/api/iip/getIIPData (frequency=Monthly).
The 2022-23 base starts April 2023; index series use it only (no splicing).
`iip_general_growth` is y/y growth as published: 2022-23 base where available,
2011-12 base before April 2023. The note column records the base of each value.
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import month_period, pages, rows

ENDPOINT = "iip/getIIPData"
# (type, category) on the 2022-23 base -> series id. sub_category "" = category total.
INDEX_SERIES = {
    ("General", "General"): "iip_general_index",
    ("Sectoral", "Mining & Quarrying"): "iip_mining_index",
    ("Sectoral", "Manufacturing"): "iip_manufacturing_index",
    ("Sectoral", "Electricity & Gas Supply"): "iip_electricity_index",
    ("Use-based category", "Primary Goods"): "iip_primary_goods_index",
    ("Use-based category", "Capital Goods"): "iip_capital_goods_index",
    ("Use-based category", "Intermediate Goods"): "iip_intermediate_goods_index",
    ("Use-based category", "Infrastructure/ Construction Goods"): "iip_infra_construction_index",
    ("Use-based category", "Consumer Durables"): "iip_consumer_durables_index",
    ("Use-based category", "Consumer Non-durables"): "iip_consumer_nondurables_index",
}


class MospiIIP(Source):
    name = "mospi_iip"
    series_ids = (*INDEX_SERIES.values(), "iip_general_growth")

    def fetch(self) -> list[Raw]:
        new = {"frequency": "Monthly", "base_year": "2022-23"}
        return (pages(ENDPOINT, {**new, "type": "General"})
                + pages(ENDPOINT, {**new, "type": "Sectoral"})
                + pages(ENDPOINT, {**new, "type": "Use-based category"})
                + pages(ENDPOINT, {"frequency": "Monthly", "base_year": "2011-12", "type": "General"}))

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        out, growth = [], {}
        for r in rows(raws):
            if r.get("sub_category"):
                continue
            period = month_period(r["year"], r["month"])
            if r["base_year"] == "2022-23":
                sid = INDEX_SERIES.get((r["type"], r["category"]))
                if sid:
                    out.append({"series_id": sid, "period": period, "value": float(r["index"])})
                if sid == "iip_general_index" and r.get("growth_rate") not in (None, ""):
                    growth[period] = (float(r["growth_rate"]), "published, base 2022-23")
            elif r["base_year"] == "2011-12" and r["type"] == "General" \
                    and r.get("growth_rate") not in (None, "") and period not in growth:
                growth[period] = (float(r["growth_rate"]), "published, base 2011-12")
        # A 2022-23 value always wins over a 2011-12 value for the same month.
        out += [{"series_id": "iip_general_growth", "period": p, "value": v, "note": n}
                for p, (v, n) in growth.items()]
        df = pd.DataFrame(out)
        df["note"] = df["note"].fillna("") if "note" in df else ""
        return df


SOURCE = MospiIIP()
