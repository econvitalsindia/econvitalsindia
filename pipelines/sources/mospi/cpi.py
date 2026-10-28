"""MoSPI Consumer Price Index (base 2024), all-India, via the eSankhyiki API.

API: GET https://api.mospi.gov.in/api/cpi/getCPIData (no key; max 100 rows/page on base 2012).
Spec: https://esankhyiki.mospi.gov.in/layout/swagger_user_cpi.yaml

Index series join MoSPI's official *back series* (2013-2024, the old series
projected onto the 2024 base by MoSPI's linking factor) to the *current series*
(2025 onwards). MoSPI does the linking; we do not splice anything ourselves.

`cpi_headline_inflation` is the y/y inflation rate **as officially published**:
2014-2024 from the back series, 2025 from the 2012-base series (the official
figure at the time; the 2024-base current series carries no 2025 inflation),
2026 onwards from the 2024-base current series. The note column says which.
"""
from __future__ import annotations

import json

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series

URL = "https://api.mospi.gov.in/api/cpi/getCPIData"
PAGE = 100
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}

# 2024-base codes (from the MoSPI MCP get_metadata call): state 1 = All India;
# sector 1 Rural, 2 Urban, 3 Combined; division 0 = CPI (General), 1 = Food and beverages.
INDEX_SERIES = {
    ("Combined", "CPI (General)"): "cpi_headline_index",
    ("Rural", "CPI (General)"): "cpi_rural_index",
    ("Urban", "CPI (General)"): "cpi_urban_index",
    ("Combined", "Food and beverages"): "cpi_food_bev_index",
}


def _period(year, month: str) -> str:
    return f"{int(year):04d}-{MONTHS[month]:02d}-01"


def months_since(last_period: str | float | None, back: int) -> dict[int, list[int]] | None:
    """{year: [months]} from `back` months before last_period up to today; None if no history."""
    if not isinstance(last_period, str) or not last_period:
        return None
    start = pd.Period(last_period[:7], freq="M") - back
    out: dict[int, list[int]] = {}
    for p in pd.period_range(start, pd.Period.now(freq="M"), freq="M"):
        out.setdefault(p.year, []).append(p.month)
    return out


def _float(x) -> float | None:
    return None if x in (None, "", "NA") else float(x)


class MospiCPI(Source):
    name = "mospi_cpi"
    series_ids = (*INDEX_SERIES.values(), "cpi_headline_inflation")

    def _pages(self, params: dict) -> list[Raw]:
        """Fetch every page of one query."""
        raws, page = [], 1
        while True:
            raw = fetch_raw(URL, params={**params, "limit": PAGE, "page": page, "Format": "JSON"})
            body = json.loads(raw.content)
            if "data" not in body:
                raise RuntimeError(f"unexpected CPI API response: {str(body)[:200]}")
            raws.append(raw)
            if page >= body["meta_data"]["totalPages"]:
                return raws
            page += 1

    def fetch(self) -> list[Raw]:
        base24 = {"base_year": "2024", "state_code": "1", "sector_code": "1,2,3"}
        raws = (self._pages({**base24, "division_code": "0", "series": "Back"})
                + self._pages({**base24, "division_code": "0", "series": "Current"}))
        # Division 1 returns every food item too (~14k rows), so after the first full
        # load fetch only the months from two before the last stored one.
        recent = months_since(load_series("cpi_food_bev_index")["period"].max(), back=2)
        food = {**base24, "division_code": "1", "series": "Current"}
        if recent is None:
            raws += self._pages(food)
        else:
            for year, months in recent.items():
                raws += self._pages({**food, "year": str(year), "month_code": ",".join(map(str, months))})
        # Official 2025 headline inflation, published on the 2012 base.
        return raws + self._pages({"base_year": "2012", "level": "Group", "series": "Current",
                                   "year": "2025", "state_code": "99", "sector_code": "3"})

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows, inflation = [], {}
        for raw in raws:
            for r in json.loads(raw.content)["data"]:
                period = _period(r["year"], r["month"])
                if r.get("base_year") == "2024":
                    sid = INDEX_SERIES.get((r["sector"], r["division"]))
                    if sid is None or r.get("group") is not None:
                        continue
                    rows.append({"series_id": sid, "period": period, "value": float(r["index"])})
                    infl = _float(r.get("inflation"))
                    if sid == "cpi_headline_index" and infl is not None:
                        inflation[period] = (infl, f"published, base 2024 {r['series'].lower()} series")
                elif r.get("baseyear") == "2012" and r.get("group") == "General" \
                        and r.get("sector") == "Combined":
                    infl = _float(r.get("inflation"))
                    # Never overwrite a 2024-base figure with a 2012-base one.
                    if infl is not None and period not in inflation:
                        inflation[period] = (infl, "published, base 2012 series")
        rows += [{"series_id": "cpi_headline_inflation", "period": p, "value": v, "note": n}
                 for p, (v, n) in inflation.items()]
        df = pd.DataFrame(rows)
        df["note"] = df.get("note", pd.Series(dtype=str)).fillna("")
        return df


SOURCE = MospiCPI()
