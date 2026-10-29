"""MoSPI National Accounts (annual, financial years), via the eSankhyiki API.

Same endpoint as nas.py with frequency_code=Annually, 2022-23 base. Each year comes with the
estimate it currently stands at ("revision": First/Second Advance, Provisional, First/Second
Revised, Final Estimates); the API serves only the latest estimate, so the note records the
stage and our revision log (data/revisions/) keeps earlier estimates as they are replaced.

Rows: indicator 22 "GDP Growth Rate" (current_price = nominal, constant_price = real);
indicator 21 "GVA Growth Rate", one row per industry; the total is "Total Gross Value
Added" and the broad sectors are the rows without a sub-industry.

Series (period = 1 April of the financial year): gdp_real_growth_fy, gdp_nominal_growth_fy,
gva_real_growth_fy. The sector panel gva_sector_growth_fy (entity = sector, real growth) is
published by nas_annual_sectors.py from the same rows (a source is either panel or not).
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import pages, rows
from pipelines.sources.mospi.nas import NEW

ENDPOINT = "nas/getNASData"
# Broad sectors as the API names them -> short names for the site.
SECTORS = {
    "Agriculture, Livestock, Forestry and Fishing": "Agriculture",
    "Mining and Quarrying": "Mining",
    "Manufacturing": "Manufacturing",
    "Electricity, Gas, Water Supply & Other Utility Services": "Utilities",
    "Construction": "Construction",
    "Trade, Hotels, Transport, Communication & Services Related to Broadcasting": "Trade, hotels, transport",
    "Financial, Real Estate & Professional Services": "Finance, real estate",
    "Public Administration, Defence & Other Services": "Public administration and other",
}


def fy_start(year: str) -> str:
    return f"{year[:4]}-04-01"


def num(v) -> float | None:
    return None if v in (None, "") else float(v)


def annual_rows(raws: list[Raw]) -> pd.DataFrame:
    out = []
    for r in rows(raws):
        period, stage = fy_start(r["year"]), r["revision"]
        if r["indicator"] == "GDP Growth Rate":
            out += [{"series_id": "gdp_real_growth_fy", "period": period, "value": num(r["constant_price"]), "note": stage},
                    {"series_id": "gdp_nominal_growth_fy", "period": period, "value": num(r["current_price"]), "note": stage}]
        elif r["indicator"] == "GVA Growth Rate" and not r.get("subindustry"):
            if r["industry"] == "Total Gross Value Added":
                out.append({"series_id": "gva_real_growth_fy", "period": period, "value": num(r["constant_price"]), "note": stage})
            elif r["industry"] in SECTORS:
                out.append({"series_id": "gva_sector_growth_fy", "entity": SECTORS[r["industry"]], "period": period,
                            "value": num(r["constant_price"]), "note": stage})
    df = pd.DataFrame(out).dropna(subset=["value"])
    if df.empty or "gdp_real_growth_fy" not in set(df["series_id"]):
        raise ValueError("MoSPI annual NAS: no GDP growth rows")
    return df


def fetch_annual() -> list[Raw]:
    q = {"frequency_code": "Annually", "base_year": NEW}
    return pages(ENDPOINT, {**q, "indicator_code": 22}) + pages(ENDPOINT, {**q, "indicator_code": 21})


class MospiNASAnnual(Source):
    name = "mospi_nas_annual"
    series_ids = ("gdp_real_growth_fy", "gdp_nominal_growth_fy", "gva_real_growth_fy")

    def fetch(self) -> list[Raw]:
        return fetch_annual()

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        df = annual_rows(raws)
        return df[df["series_id"].isin(self.series_ids)].drop(columns="entity", errors="ignore")


SOURCE = MospiNASAnnual()
