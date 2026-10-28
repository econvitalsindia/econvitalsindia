"""Union Government monthly accounts ("Accounts at a Glance"), Controller General of Accounts.

Page per month: https://cga.nic.in/writereaddata/MonthAccount/<m><yyyy>/DATA<fy>.htm
(m = month number without padding, fy = e.g. 2627 for 2026-27; some months use .HTM).
Columns: Budget Estimates, Actuals up to the month (₹ crore, financial year to date),
% of BE (current year) and % of BE in the corresponding period of the previous year.
Figures are year-to-date; period = the month the accounts run to. Stored in ₹ lakh crore.
"""
from __future__ import annotations

import io
import re
from html import unescape

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series

URL = "https://cga.nic.in/writereaddata/MonthAccount/{m}{y}/DATA{fy}.{ext}"
FIRST_MONTH = pd.Period("2024-04", freq="M")
RECENT_MONTHS, MIN_HISTORY = 3, 12
# Row label (start, spaces collapsed) -> series prefix
ROWS = {
    "Revenue Receipts": "cga_revenue_receipts", "Tax Revenue (Net)": "cga_net_tax",
    "Total Receipts": "cga_total_receipts", "Revenue Expenditure": "cga_revenue_expenditure",
    "of which Interest Payments": "cga_interest", "Capital Expenditure": "cga_capex",
    "Total Expenditure": "cga_total_expenditure", "Fiscal Deficit": "cga_fiscal_deficit",
    "Revenue Deficit": "cga_revenue_deficit", "Primary Deficit": "cga_primary_deficit",
}
# Rows whose "% of BE" (current and previous year) are also stored.
PCT_BE = {"Fiscal Deficit": "cga_fiscal_deficit", "Capital Expenditure": "cga_capex",
          "Tax Revenue (Net)": "cga_net_tax"}


def fy_code(p: pd.Period) -> str:
    start = p.year if p.month >= 4 else p.year - 1
    return f"{start % 100:02d}{(start + 1) % 100:02d}"


def pct(x) -> float | None:
    m = re.search(r"-?\d+(\.\d+)?", str(x))
    return float(m.group(0)) if m else None


def number(x) -> float:
    """'3 087960' / '1,292,470' -> float (the pages use stray spaces as separators)."""
    return float(re.sub(r"[\s,]", "", str(x)))


def parse_glance(html: str) -> tuple[str, list[dict], str]:
    """(period, rows, basis) from one month's 'Accounts at a Glance' page.

    basis is "BE" normally; March pages compare provisional actuals with Revised
    Estimates ("RE"), so their % columns are % of RE.
    """
    text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))
    m = re.search(r"AS AT THE END OF\s+([A-Za-z]+),?\s+(\d{4})", text, re.I)
    if m:
        period = pd.Period(f"{m.group(1)[:3]} {m.group(2)}", freq="M").strftime("%Y-%m-01")
    else:
        # March pages: "PROVISIONAL ACCOUNTS FOR 2024- 2025" = the full year, to March 2025.
        m = re.search(r"PROVISIONAL ACCOUNTS FOR\s+(\d{4})\s*-\s*(\d{4})", text, re.I)
        if not m:
            raise ValueError("no 'as at the end of <Month> <Year>' or 'provisional accounts for' heading")
        period = f"{m.group(2)}-03-01"
    basis = "RE" if "Revised Estimates" in text[:3000] else "BE"
    table = next(t for t in pd.read_html(io.StringIO(html)) if t.shape[1] >= 7)
    rows = []
    for _, r in table.iterrows():
        label = re.sub(r"\s+", " ", str(r[1])).strip()
        key = next((k for k in ROWS if label.startswith(k)), None)
        if key is None:
            continue
        prefix = ROWS[key]
        rows.append({"series_id": f"{prefix}_fytd", "period": period, "value": round(number(r[4]) / 1e5, 4)})
        if key in PCT_BE:
            rows.append({"series_id": f"{prefix}_pct_be", "period": period, "value": pct(r[5])})
            rows.append({"series_id": f"{prefix}_pct_be_prev", "period": period, "value": pct(r[6])})
    if not rows:
        raise ValueError("no recognised rows in accounts table")
    return period, rows, basis


class CgaMonthlyAccounts(Source):
    name = "cga_monthly_accounts"
    series_ids = (*(f"{p}_fytd" for p in ROWS.values()),
                  *(f"{p}_{s}" for p in PCT_BE.values() for s in ("pct_be", "pct_be_prev")))

    def fetch(self) -> list[Raw]:
        now = pd.Period.now(freq="M")
        backfill = len(load_series("cga_fiscal_deficit_fytd")) < MIN_HISTORY
        start = FIRST_MONTH if backfill else now - RECENT_MONTHS
        raws = []
        for p in pd.period_range(start, now, freq="M"):
            for ext in ("htm", "HTM"):
                try:
                    raws.append(fetch_raw(URL.format(m=p.month, y=p.year, fy=fy_code(p), ext=ext),
                                          suffix=".htm"))
                    break
                except RuntimeError as e:
                    if "404" not in str(e):
                        raise
        if not raws:
            raise RuntimeError("no CGA monthly accounts pages found")
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            _, r, basis = parse_glance(raw.content.decode("utf-8", errors="ignore"))
            note = ("financial year to date" if basis == "BE"
                    else "full year, provisional actuals; % columns are % of Revised Estimates")
            rows += [{**x, "note": note} for x in r]
        return pd.DataFrame(rows).dropna(subset=["value"])


SOURCE = CgaMonthlyAccounts()
