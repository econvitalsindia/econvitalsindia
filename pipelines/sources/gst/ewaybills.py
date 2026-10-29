"""E-way bills, monthly, all-India, from the GST portal's statistics workbooks.

Files: https://tutorial.gst.gov.in/offlineutilities/gst_statistics/ewb-data-<YYYY-YY>.xlsx
(linked from https://www.gst.gov.in/download/gststatistics), one per financial year from
2018-19 (which starts in July 2018). One row per state and month: state code, name, year,
month, then three blocks of (suppliers, number of e-way bills, assessable value Rs crore):
within the state, outgoing to other states, incoming from other states.

All-India = sum over states of within-state + outgoing. Incoming bills are other states'
outgoing bills, so adding them would count inter-state movements twice. The current year's
file is updated in place; the newest download wins.

Series: ewaybills_count (crore e-way bills), ewaybills_value (Rs lakh crore).
"""
from __future__ import annotations

import io
from datetime import date

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series

URL = "https://tutorial.gst.gov.in/offlineutilities/gst_statistics/ewb-data-{fy}.xlsx"
FIRST_FY = 2018
# Column positions: 0 code, 1 state, 2 year, 3 month, 4-6 within, 7-9 outgoing, 10-12 incoming.
WITHIN_N, WITHIN_V, OUT_N, OUT_V = 5, 6, 8, 9


def fy_label(start: int) -> str:
    return f"{start}-{str(start + 1)[2:]}"


def parse_workbook(df: pd.DataFrame) -> list[dict]:
    rows = df[pd.to_numeric(df[0], errors="coerce").notna() & pd.to_numeric(df[2], errors="coerce").notna()]
    if rows.empty:
        raise ValueError("no state rows in the e-way bill workbook")
    num = rows[[2, 3, WITHIN_N, WITHIN_V, OUT_N, OUT_V]].apply(pd.to_numeric, errors="coerce")
    g = num.groupby([2, 3]).sum()
    out = []
    for (y, m), r in g.iterrows():
        period = f"{int(y)}-{int(m):02d}-01"
        out.append({"series_id": "ewaybills_count", "period": period,
                    "value": round((r[WITHIN_N] + r[OUT_N]) / 1e7, 4)})
        out.append({"series_id": "ewaybills_value", "period": period,
                    "value": round((r[WITHIN_V] + r[OUT_V]) / 1e5, 4)})
    return out


class EwayBills(Source):
    name = "gst_ewaybills"
    series_ids = ("ewaybills_count", "ewaybills_value")

    def fetch(self) -> list[Raw]:
        today = date.today()
        current = today.year if today.month >= 4 else today.year - 1
        backfill = len(load_series("ewaybills_count")) < 24
        years = range(FIRST_FY if backfill else current - 1, current + 1)
        return [fetch_raw(URL.format(fy=fy_label(y)), suffix=".xlsx") for y in years]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            rows += parse_workbook(pd.read_excel(io.BytesIO(raw.content), sheet_name=0, header=None))
        out = pd.DataFrame(rows).drop_duplicates(["series_id", "period"], keep="last")
        out["note"] = "sum over states: within-state + outgoing"
        return out


SOURCE = EwayBills()
