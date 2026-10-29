"""Mutual fund flows, monthly, from AMFI's monthly report.

AMFI's page https://www.amfiindia.com/research-information/amfi-monthly links one report per
month as PDF and, from April 2018, as XLS (read from April 2019; see FIRST):
  https://portal.amfiindia.com/spages/am<mon><yyyy>repo.xls  ("...reporevised.xls" sometimes)
Sheet 1 is one row per scheme category; the header names the month ("Net Inflow (+ve)/Outflow
(-ve) for the month of September 2026 (INR in crore)") and the columns are found by header
text. Rows used (open-ended schemes come first, so the first match is open-ended):
  "Sub Total - I"   debt schemes          "Sub Total - II"  equity schemes
  "Grand Total"     all schemes (net inflow and net assets under management)
AMFI does not revise past reports; the first run reads every XLS, later runs the newest few.

Series: mf_net_inflow_total, mf_net_inflow_equity, mf_net_inflow_debt (Rs crore a month),
mf_aum_total (Rs lakh crore, end of month).
"""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series

PAGE = "https://www.amfiindia.com/research-information/amfi-monthly"
RECENT, MIN_HISTORY = 3, 24
# Reports before April 2019 have another layout (no "Net Inflow" header row); not read.
FIRST = "2019-04"
ROWS = {"Sub Total - I": "mf_net_inflow_debt", "Sub Total - II": "mf_net_inflow_equity",
        "Grand Total": "mf_net_inflow_total"}


def parse_report(content: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None)
    head = df.index[df.apply(lambda r: r.astype(str).str.contains("Net Inflow").any(), axis=1)][0]
    hdr = df.loc[head].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()   # older files break lines
    net_col = next(c for c in df.columns if "Net Inflow" in hdr[c])
    aum_col = next(c for c in df.columns if hdr[c].startswith(("Net Assets Under Management", "AUM as on")))
    m = re.search(r"for the month of\s+([A-Za-z]+),?\s*(\d{4})", hdr[net_col])
    period = datetime.strptime(f"{m.group(1)[:3]} {m.group(2)}", "%b %Y").strftime("%Y-%m-01")
    labels = df.apply(lambda r: " ".join(str(v).strip() for v in r[:3] if isinstance(v, str)), axis=1)
    rows, seen = [], set()
    for i, label in labels.items():
        key = next((k for k in ROWS if re.sub(r"\s+", " ", label).strip().startswith(k)
                    and not re.sub(r"\s+", " ", label).strip().startswith(k + "I")), None)
        if key and key not in seen:
            seen.add(key)
            rows.append({"series_id": ROWS[key], "period": period, "value": round(float(df.loc[i, net_col]), 2)})
            if key == "Grand Total":
                rows.append({"series_id": "mf_aum_total", "period": period, "value": round(float(df.loc[i, aum_col]) / 1e5, 4)})
    if len(seen) < len(ROWS):
        raise ValueError(f"AMFI {period}: rows not found: {set(ROWS) - seen}")
    return rows


class AmfiMonthly(Source):
    name = "amfi_monthly"
    series_ids = (*ROWS.values(), "mf_aum_total")

    def fetch(self) -> list[Raw]:
        page = get(PAGE).text
        links = list(dict.fromkeys(re.findall(r"https://portal\.amfiindia\.com/spages/am[a-z]{3}\d{4}repo(?:revised)?\.xls", page)))
        if not links:
            raise RuntimeError("no AMFI monthly XLS reports linked")
        def month(u: str) -> str:
            m = re.search(r"am([a-z]{3})(\d{4})repo", u)
            return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%b %Y").strftime("%Y-%m")
        links = [u for u in links if month(u) >= FIRST]
        take = links if len(load_series("mf_net_inflow_total")) < MIN_HISTORY else links[:RECENT]
        return [fetch_raw(u, suffix=".xls") for u in take]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            rows += parse_report(raw.content)
        out = pd.DataFrame(rows).drop_duplicates(["series_id", "period"], keep="first")
        out["note"] = "AMFI monthly report"
        return out


SOURCE = AmfiMonthly()
