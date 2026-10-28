"""MoSPI National Accounts (quarterly), all-India, via the eSankhyiki API.

API: GET https://api.mospi.gov.in/api/nas/getNASData (frequency_code=Quarterly).
Indicator codes (MCP get_indicators "NAS"): 5 GDP, 9 GFCF, 10 PFCE, 11 GFCE,
14 exports, 15 imports, 21 GVA growth rate, 22 GDP growth rate.

- Growth rates are as published: 2022-23 base from Q1 FY24, 2011-12 base before
  (note column records the base). Real = constant prices.
- Levels are on the 2022-23 base only, converted from ₹ crore to ₹ lakh crore.
Quarters are financial-year quarters; period = first day of the quarter
(Q1 FY27 = Apr-Jun 2026 -> 2026-04-01).
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import pages, rows

ENDPOINT = "nas/getNASData"
NEW, OLD = "2022-23", "2011-12"
# indicator code -> (name as returned by the API, series prefix)
LEVELS = {5: ("Gross Domestic Product", "gdp"),
          10: ("Private Final Consumption Expenditure", "pfce"),
          11: ("Government Final Consumption Expenditure", "gfce"),
          9: ("Gross Fixed Capital Formation", "gfcf"),
          14: ("Export of Goods and Services", "exports"),
          15: ("Import of Goods and Services", "imports")}
LEVEL_PREFIX = dict(LEVELS.values())
SECTORS = {
    "Agriculture, Livestock, Forestry and Fishing": "gva_agri_growth",
    "Mining and Quarrying": "gva_mining_growth",
    "Manufacturing": "gva_mfg_growth",
    "Electricity, Gas, Water Supply & Other Utility Services": "gva_utilities_growth",
    "Construction": "gva_construction_growth",
    "Trade, Hotels, Transport, Communication & Services Related to Broadcasting": "gva_trade_growth",
    "Financial, Real Estate & Professional Services": "gva_finance_growth",
    "Public Administration, Defence & Other Services": "gva_public_growth",
}
# The total row is labelled differently on the two bases.
TOTAL_GVA = {"Total Gross Value Added", "Total GVA Growth Rate"}


def lakh_crore(crore) -> float | None:
    return None if crore in (None, "") else float(crore) / 1e5


def quarter_period(fy: str, quarter: str) -> str:
    """("2026-27", "Q1") -> "2026-04-01"; Q4 falls in the next calendar year."""
    start = int(fy[:4])
    q = int(quarter.strip("Q"))
    year, month = (start, 3 * q + 1) if q < 4 else (start + 1, 1)
    return f"{year:04d}-{month:02d}-01"


class MospiNAS(Source):
    name = "mospi_nas"
    series_ids = (
        "gdp_real_growth", "gdp_nominal_growth", "gva_real_growth", *SECTORS.values(),
        "gdp_real_level", "gdp_nominal_level",
        *(f"{prefix}_real_level" for _, prefix in LEVELS.values() if prefix != "gdp"),
    )

    def fetch(self) -> list[Raw]:
        q = {"series": "Current", "frequency_code": "Quarterly"}
        raws = []
        for base in (NEW, OLD):
            raws += pages(ENDPOINT, {**q, "base_year": base, "indicator_code": 22})
            raws += pages(ENDPOINT, {**q, "base_year": base, "indicator_code": 21})
        for code in LEVELS:
            raws += pages(ENDPOINT, {**q, "base_year": NEW, "indicator_code": code})
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        found: dict[tuple[str, str], tuple[float, str]] = {}

        def put(sid, period, value, base, note=""):
            # The 2022-23 base wins over 2011-12 for the same quarter.
            key = (sid, period)
            if value in (None, "") or (key in found and base == OLD):
                return
            found[key] = (float(value), note)

        for r in rows(raws):
            if r.get("frequency") != "Quarterly" or not r.get("quarter"):
                continue
            base, period = r["base_year"], quarter_period(r["year"], r["quarter"])
            note = f"published, base {base}"
            ind = r["indicator"]
            if ind == "GDP Growth Rate":
                put("gdp_real_growth", period, r["constant_price"], base, note)
                put("gdp_nominal_growth", period, r["current_price"], base, note)
            elif ind == "GVA Growth Rate":
                if r.get("industry") in TOTAL_GVA:
                    put("gva_real_growth", period, r["constant_price"], base, note)
                elif r.get("industry") in SECTORS and not r.get("subindustry"):
                    put(SECTORS[r["industry"]], period, r["constant_price"], base, note)
            elif base == NEW and ind in LEVEL_PREFIX \
                    and not r.get("industry") and not r.get("institutional_sector"):
                prefix = LEVEL_PREFIX[ind]
                put(f"{prefix}_real_level", period, lakh_crore(r["constant_price"]), base)
                if prefix == "gdp":
                    put("gdp_nominal_level", period, lakh_crore(r["current_price"]), base)

        return pd.DataFrame([{"series_id": s, "period": p, "value": v, "note": n}
                             for (s, p), (v, n) in found.items()])


SOURCE = MospiNAS()
