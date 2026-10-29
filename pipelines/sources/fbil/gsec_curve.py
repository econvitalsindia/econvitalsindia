"""Government bond par yield curve, daily, from FBIL.

FBIL's site lists its daily "GOI Prices including Par Yield" files at
  https://www.fbil.org.in/wasdm/gsec/fetchfiltered?fromDate=YYYY-MM-DD&toDate=YYYY-MM-DD&authenticated=false
(JSON: [{"processRunDate": "2026-10-22", ...}]) and serves each as an XLSX at
  https://www.fbil.org.in/wasdm/gsec/downloadPublished?date=YYYY-MM-DD
(the calls FBIL's own page makes). Sheet "Par Yield": tenor in years (0.25 to 50) and the
par yield, % p.a. semi-annual (the market convention; an annualised column follows).
The public files lag publication by about a week.

One panel: gsec_par_yield, entity = tenor ("3m", "1y", ... "40y"), period = date. The first
run backfills from FIRST_DATE; later runs look at the last RECENT_DAYS and download only days not stored yet.
"""
from __future__ import annotations

import io
from datetime import date, timedelta

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_panel

BASE = "https://www.fbil.org.in/wasdm/gsec"
FIRST_DATE, RECENT_DAYS, MIN_DATES = "2025-01-01", 30, 100
TENORS = {0.25: "3m", 0.5: "6m", 1: "1y", 2: "2y", 3: "3y", 5: "5y", 7: "7y", 10: "10y",
          15: "15y", 20: "20y", 30: "30y", 40: "40y"}


def parse_par_yield(content: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(content), sheet_name="Par Yield", header=None)
    stamp = next(v for v in df.head(5).values.ravel() if isinstance(v, str) and v[:2].isdigit() and "-" in v)
    day = pd.to_datetime(stamp, format="%d-%b-%Y").date().isoformat()
    tenor = pd.to_numeric(df[0], errors="coerce")
    rows = []
    for t, label in TENORS.items():
        hit = df[tenor == t]
        if not hit.empty and pd.notna(hit.iloc[0, 1]):
            rows.append({"series_id": "gsec_par_yield", "entity": label, "period": day, "value": float(hit.iloc[0, 1])})
    if len(rows) < len(TENORS) - 2:
        raise ValueError(f"FBIL par yield file for {day}: only {len(rows)} tenors found")
    return rows


class FbilGsecCurve(Source):
    name = "fbil_gsec_curve"
    panel = True
    series_ids = ("gsec_par_yield",)

    def fetch(self) -> list[Raw]:
        have = load_panel("gsec_par_yield")
        start = FIRST_DATE if have["period"].nunique() < MIN_DATES else (date.today() - timedelta(days=RECENT_DAYS)).isoformat()
        listed = {d["processRunDate"] for d in get(
            f"{BASE}/fetchfiltered?fromDate={start}&toDate={date.today().isoformat()}&authenticated=false").json()}
        if not listed:
            raise RuntimeError("FBIL listed no G-sec files")
        # Published files don't change: take the days not stored yet, plus the newest one.
        days = sorted(listed - set(have["period"]) | {max(listed)})
        return [fetch_raw(f"{BASE}/downloadPublished?date={d}", suffix=".xlsx") for d in days]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            rows += parse_par_yield(raw.content)
        out = pd.DataFrame(rows).drop_duplicates(["entity", "period"], keep="last")
        out["note"] = ""
        return out


SOURCE = FbilGsecCurve()
