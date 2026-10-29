"""Union Budget headline numbers, from "Budget at a Glance" (indiabudget.gov.in).

File: https://www.indiabudget.gov.in/doc/Budget_at_Glance/budget_at_a_glance.xlsx, replaced
each Budget. Sheet "BAAG" has the headline table and "Deficit Statistics" the deficits with
% of GDP in brackets on the row below each figure. Both have four columns, read from the two
header rows: Actuals (two years back), Budget Estimates and Revised Estimates (last year),
Budget Estimates (the Budget year), e.g. 2024-2025 Actuals | 2025-2026 BE | 2025-2026 RE |
2026-2027 BE. Rows are matched by their English label ("17. Fiscal Deficit [9-(1+5+6)]").

Three panels, one per stage, entity = budget item, period = first day of the financial
year (2026-27 -> 2026-04-01). Amounts in Rs lakh crore (Rs crore in the file), deficit
ratios in % of GDP. Each new Budget adds a year, so history builds up from 2024-25.
"""
from __future__ import annotations

import io
import re

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://www.indiabudget.gov.in/doc/Budget_at_Glance/budget_at_a_glance.xlsx"
STAGES = {"Actuals": "budget_actuals", "Budget": "budget_be", "Revised": "budget_re"}
# English label in the file -> entity name on the site (amounts, Rs lakh crore).
AMOUNTS = {
    "Revenue Receipts": "Revenue receipts", "Tax Revenue (Net to Centre)": "Tax revenue (net to Centre)",
    "Non Tax Revenue": "Non-tax revenue", "Total Expenditure": "Total expenditure",
    "On Revenue Account": "Revenue expenditure", "Interest Payments": "Interest payments",
    "On Capital Account": "Capital expenditure", "Effective Capital Expenditure": "Effective capital expenditure",
    "Fiscal Deficit": "Fiscal deficit", "Revenue Deficit": "Revenue deficit", "Primary Deficit": "Primary deficit",
}
RATIOS = {"Fiscal Deficit": "Fiscal deficit, % of GDP", "Revenue Deficit": "Revenue deficit, % of GDP",
          "Primary Deficit": "Primary deficit, % of GDP"}
ORDER = [*AMOUNTS.values(), *RATIOS.values()]


def english(cell) -> str | None:
    """'17. Fiscal Deficit [9-(1+5+6)]' -> 'Fiscal Deficit [9-(1+5+6)]'."""
    m = re.match(r"^\s*\d+\.\s+([A-Za-z].*)", str(cell).replace("\n", " "))
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def columns(df: pd.DataFrame) -> dict[int, tuple[str, str]]:
    """{column: (panel id, 'YYYY-04-01')} from the year row and the stage row below it."""
    year_row = next(i for i in df.index if sum(bool(re.fullmatch(r"\d{4}-\d{4}", str(v).strip())) for v in df.loc[i]) >= 3)
    out = {}
    for c in df.columns:
        y = str(df.loc[year_row, c]).strip()
        stage = next((sid for word, sid in STAGES.items() if word in str(df.loc[year_row + 1, c])), None)
        if re.fullmatch(r"\d{4}-\d{4}", y) and stage:
            out[c] = (stage, f"{y[:4]}-04-01")
    if len(out) < 3:
        raise ValueError("Budget at a Glance: year/stage header not found")
    return out


def parse_sheet(df: pd.DataFrame, wanted: dict[str, str], ratio: bool) -> list[dict]:
    cols = columns(df)
    rows = []
    for i in df.index:
        label = next((english(v) for v in df.loc[i] if english(v)), None)
        entity = next((name for key, name in wanted.items() if label and label.startswith(key)), None)
        if not entity:
            continue
        source = df.loc[i + 1] if ratio else df.loc[i]
        for c, (sid, period) in cols.items():
            v = str(source[c]).strip().strip("()")
            if re.fullmatch(r"-?\d+(\.\d+)?", v):
                value = float(v) if ratio else round(float(v) / 1e5, 4)
                rows.append({"series_id": sid, "entity": entity, "period": period, "value": value})
    return rows


class BudgetGlance(Source):
    name = "budget_glance"
    panel = True
    series_ids = tuple(STAGES.values())

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL, suffix=".xlsx")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        book = pd.ExcelFile(io.BytesIO(raws[0].content))
        rows = parse_sheet(pd.read_excel(book, "BAAG", header=None), AMOUNTS, ratio=False)
        rows += parse_sheet(pd.read_excel(book, "Deficit Statistics", header=None), RATIOS, ratio=True)
        missing = set(ORDER) - {r["entity"] for r in rows}
        if missing:
            raise ValueError(f"Budget at a Glance rows not found: {sorted(missing)}")
        out = pd.DataFrame(rows)
        out["note"] = ""
        return out


SOURCE = BudgetGlance()
