"""UPI transactions, monthly, from RBI's Payment System Indicators (PSI).

NPCI's own statistics pages refuse scripted requests, so UPI comes from RBI, which reprints
it. The PSI page (https://www.rbi.org.in/Scripts/PSIUserView.aspx) links one XLSX per month
(the last twelve). Each has volume (lakh) and value (Rs crore) for the financial year to
date, the same month a year earlier, the previous month and the month itself:
    row:  "Volume (lakh)" ... "Value (₹ crore)"
    row:  FY 2025-26 | 2025\\nSeptember | 2026    | 2026
    row:             |                 | August  | September
UPI is the row "2.6 UPI @". Later files revise earlier months; files arrive newest first and
the first value seen for a month wins.

Series: upi_volume (crore transactions), upi_value (Rs lakh crore).
"""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get

PAGE = "https://www.rbi.org.in/Scripts/PSIUserView.aspx"
ROW = "2.6 UPI"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def column_months(df: pd.DataFrame, head: int) -> dict[int, str]:
    """{column: 'YYYY-MM-01'} for the month columns under the header row."""
    out, year = {}, None
    for c in df.columns:
        top, below = str(df.loc[head + 1, c]), str(df.loc[head + 2, c])
        if top.startswith("FY"):
            year = None
            continue
        y = re.search(r"\b(20\d\d)\b", top)
        year = int(y.group(1)) if y else year
        m = re.search(MONTHS, top) or re.search(MONTHS, below)
        if year and m:
            out[c] = datetime.strptime(f"{m.group(0)} {year}", "%B %Y").strftime("%Y-%m-01")
    return out


def parse_psi(df: pd.DataFrame) -> list[dict]:
    head = df.index[df.apply(lambda r: r.astype(str).str.contains("Volume \\(lakh\\)").any(), axis=1)][0]
    value_col = next(c for c in df.columns if "Value" in str(df.loc[head, c]))
    months = column_months(df, head)
    labels = df.apply(lambda r: " ".join(str(v) for v in r if isinstance(v, str)).strip(), axis=1)
    row = df.loc[labels[labels.str.startswith(ROW)].index[0]]
    rows = []
    for c, period in months.items():
        if pd.isna(row[c]):
            continue
        if c < value_col:
            rows.append({"series_id": "upi_volume", "period": period, "value": round(float(row[c]) / 100, 4)})
        else:
            rows.append({"series_id": "upi_value", "period": period, "value": round(float(row[c]) / 1e5, 4)})
    return rows


class RbiPayments(Source):
    name = "rbi_payments"
    series_ids = ("upi_volume", "upi_value")

    def fetch(self) -> list[Raw]:
        page = get(PAGE).text
        links = list(dict.fromkeys(re.findall(r"https://rbidocs\.rbi\.org\.in/rdocs/PSI/DOCs/[^\"']+\.XLSX", page, re.I)))
        if not links:
            raise RuntimeError("no PSI workbooks linked on the RBI page")
        return [fetch_raw(u, suffix=".xlsx") for u in links]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            df = pd.read_excel(io.BytesIO(raw.content), sheet_name=0, header=None)
            rows += parse_psi(df)
        out = pd.DataFrame(rows).drop_duplicates(["series_id", "period"], keep="first")
        out["note"] = "RBI Payment System Indicators"
        return out


SOURCE = RbiPayments()
