"""All-India power supply position, daily, from Grid-India's Daily PSP reports.

File list: POST https://webapi.grid-india.in/api/v1/file
  {"_source": "GRDW", "_type": "DAILY_PSP_REPORT", "_fileDate": "<FY e.g. 2026-27>", "_month": "00"}
Files: https://webcdn.grid-india.in/<FilePath> (one .xls and one .pdf per day; we use the .xls).
Each report covers the previous day ("27.10.26_NLDC_PSP" = data for 27 Oct 2026). Sheet
MOP_E, section A: all-India TOTAL column for energy met, maximum demand met, solar and
wind generation.

fetch: manual. Grid-India refused GitHub's US runners in the reachability probe, so this
runs from India via `make india-update`. The first run backfills from BACKFILL_FROM;
later runs fetch only days after the last stored one (re-reading the last few).
"""
from __future__ import annotations

import io
import re
from datetime import date, timedelta

import httpx
import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import HEADERS, fetch_raw
from pipelines.core.store import load_series

API = "https://webapi.grid-india.in/api/v1/file"
CDN = "https://webcdn.grid-india.in/"
BACKFILL_FROM = date(2025, 4, 1)
REFRESH_DAYS = 3
ROWS = {  # row label prefix in section A -> (series id, scale)
    "Energy Met (MU)": ("power_energy_met", 1),
    "Maximum Demand Met During the Day": ("power_peak_demand", 1 / 1000),  # MW -> GW
    "Solar Gen": ("power_solar_gen", 1),
    "Wind Gen": ("power_wind_gen", 1),
}


def fy_of(d: date) -> str:
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{(start + 1) % 100:02d}"


def data_date(title: str) -> date | None:
    """'27.10.26_NLDC_PSPNEW' -> 2026-10-27."""
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{2})", title)
    return date(2000 + int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def parse_psp(content: bytes) -> dict[str, float]:
    df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None)
    labels = df[0].astype(str).str.strip()
    total_row = df.index[df.apply(lambda r: (r.astype(str).str.strip() == "TOTAL").any(), axis=1)][0]
    total_col = next(c for c in df.columns if str(df.at[total_row, c]).strip() == "TOTAL")
    out = {}
    for prefix, (sid, scale) in ROWS.items():
        hit = df.index[labels.str.startswith(prefix)]
        if len(hit):
            v = pd.to_numeric(df.at[hit[0], total_col], errors="coerce")
            if pd.notna(v):
                out[sid] = round(float(v) * scale, 3)
    if "power_energy_met" not in out:
        raise ValueError("Energy Met row not found in PSP report")
    return out


class GridIndiaPSP(Source):
    name = "gridindia_psp"
    series_ids = tuple(sid for sid, _ in ROWS.values())

    def _list(self, fy: str) -> list[dict]:
        r = httpx.post(API, json={"_source": "GRDW", "_type": "DAILY_PSP_REPORT", "_fileDate": fy, "_month": "00"},
                       headers={**HEADERS, "Content-Type": "application/json"}, timeout=60)
        r.raise_for_status()
        return r.json()["retData"]

    def fetch(self) -> list[Raw]:
        stored = load_series("power_energy_met")["period"]
        start = (date.fromisoformat(stored.max()) - timedelta(days=REFRESH_DAYS)
                 if len(stored) else BACKFILL_FROM)
        fys = sorted({fy_of(start), fy_of(date.today())})
        files = {}
        for fy in fys:
            for item in self._list(fy):
                d = data_date(item["Title_"])
                if d and d >= start and item["FilePath"].lower().endswith((".xls", ".xlsx")):
                    if d not in files or item["Id"] > files[d]["Id"]:   # keep the latest upload per day
                        files[d] = item
        raws = []
        for d, item in sorted(files.items()):
            raw = fetch_raw(CDN + item["FilePath"], suffix=".xls")
            raw.url = f"{raw.url}#date={d.isoformat()}"
            raws.append(raw)
        if not raws and not len(stored):
            raise RuntimeError("no Grid-India PSP files listed")
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            d = raw.url.split("#date=")[1]
            for sid, v in parse_psp(raw.content).items():
                rows.append({"series_id": sid, "period": d, "value": v, "note": "Grid-India daily PSP"})
        return pd.DataFrame(rows, columns=["series_id", "period", "value", "note"])


SOURCE = GridIndiaPSP()
