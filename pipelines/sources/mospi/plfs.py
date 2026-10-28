"""MoSPI Periodic Labour Force Survey, monthly bulletin (current weekly status), all-India.

API: GET https://api.mospi.gov.in/api/plfs/getData with frequency_code=3 (monthly,
from 2025; indicators 1 LFPR, 2 WPR, 3 UR only). indicator_code takes ONE value per
call. Values are percentages as published (CWS).
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import month_period, pages, rows

ENDPOINT = "plfs/getData"
INDICATORS = {1: "lfpr", 2: "wpr", 3: "ur"}
AGES = {1: "15 years and above", 2: "15-29 years"}
# (indicator, age, gender, sector) -> series id
SERIES = {
    ("ur", "15 years and above", "person", "rural + urban"): "plfs_ur_monthly",
    ("ur", "15 years and above", "person", "rural"): "plfs_ur_rural_monthly",
    ("ur", "15 years and above", "person", "urban"): "plfs_ur_urban_monthly",
    ("ur", "15 years and above", "female", "rural + urban"): "plfs_ur_female_monthly",
    ("ur", "15-29 years", "person", "rural + urban"): "plfs_ur_youth_monthly",
    ("lfpr", "15 years and above", "person", "rural + urban"): "plfs_lfpr_monthly",
    ("lfpr", "15 years and above", "female", "rural + urban"): "plfs_lfpr_female_monthly",
    ("wpr", "15 years and above", "person", "rural + urban"): "plfs_wpr_monthly",
}
NAMES = {"LFPR": "lfpr", "WPR": "wpr", "UR ": "ur"}


class MospiPLFS(Source):
    name = "mospi_plfs"
    series_ids = tuple(SERIES.values())

    def fetch(self) -> list[Raw]:
        raws = []
        for code in INDICATORS:
            for age in AGES:
                raws += pages(ENDPOINT, {"indicator_code": code, "frequency_code": 3, "age_code": age})
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        out = []
        for r in rows(raws):
            if r.get("frequency") != "Monthly" or r.get("state") != "All India":
                continue
            ind = next((v for k, v in NAMES.items() if r["indicator"].startswith(k)), None)
            sid = SERIES.get((ind, r["AgeGroup"], r["gender"], r["sector"]))
            if sid and r.get("value") not in (None, ""):
                out.append({"series_id": sid, "period": month_period(r["year"], r["month"]),
                            "value": float(r["value"]), "note": "CWS, published"})
        return pd.DataFrame(out)


SOURCE = MospiPLFS()
