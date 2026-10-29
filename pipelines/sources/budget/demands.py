"""Union Budget spending by ministry and department, from the Expenditure Profile.

File: https://www.indiabudget.gov.in/doc/eb/stat3a.xlsx ("Statement 3: Expenditure of
Ministries and Departments", Rs crore), replaced each Budget. One block per demand for
grants, headed "Demand No. 1\\nDepartment of Agriculture and Farmers Welfare", followed by
its scheme rows. The header has four groups (Actuals Y-2, Budget Estimates Y-1, Revised
Estimates Y-1, Budget Estimates Y), each with Revenue | Capital | Total; we keep Total.
Check: the demands add up to the statement's "Grand Total" in every column.

Three panels (entity = demand, e.g. "Ministry of Railways"; period = 1 April of the year;
Rs lakh crore): budget_demand_actuals, budget_demand_be, budget_demand_re.
"""
from __future__ import annotations

import io
import re

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://www.indiabudget.gov.in/doc/eb/stat3a.xlsx"
STAGES = {"Actuals": "budget_demand_actuals", "Budget Estimates": "budget_demand_be",
          "Revised Estimates": "budget_demand_re"}


def total_columns(df: pd.DataFrame) -> dict[int, tuple[str, str]]:
    """{column of 'Total': (panel id, 'YYYY-04-01')} from the two header rows."""
    head = df.index[df.apply(lambda r: r.astype(str).str.contains(r"Estimates \d{4}-\d{4}").any(), axis=1)][0]
    groups, current = {}, None
    for c in df.columns:
        m = re.search(r"(Actuals|Budget Estimates|Revised Estimates)\s+(\d{4})-\d{4}", str(df.loc[head, c]))
        if m:
            current = (STAGES[m.group(1)], f"{m.group(2)}-04-01")
        if current and str(df.loc[head + 1, c]).strip() == "Total":
            groups[c] = current
    if len(groups) != 4:
        raise ValueError(f"Statement 3: expected 4 Total columns, found {len(groups)}")
    return groups


def parse_statement(content: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None)
    cols = total_columns(df)
    label_col = 1
    rows, grand = [], None
    for i in df.index:
        label = str(df.loc[i, label_col])
        m = re.match(r"Demand No\.\s*(\d+)\s*\n?\s*(.+)", label, re.S)
        if m:
            name = re.sub(r"\s+", " ", m.group(2)).strip()
            for c, (sid, period) in cols.items():
                v = pd.to_numeric(df.loc[i, c], errors="coerce")
                rows.append({"series_id": sid, "entity": name, "period": period,
                             "value": 0.0 if pd.isna(v) else round(float(v) / 1e5, 5), "demand": int(m.group(1))})
        elif label.strip() == "Grand Total":
            grand = {c: float(df.loc[i, c]) / 1e5 for c in cols}
    if not rows or grand is None:
        raise ValueError("Statement 3: no demands or no Grand Total")
    out = pd.DataFrame(rows)
    for c, (sid, period) in cols.items():
        total = out[(out.series_id == sid) & (out.period == period)]["value"].sum()
        if abs(total - grand[c]) > 0.01:                         # Rs 1,000 crore
            raise ValueError(f"Statement 3: demands add to {total:.3f} lakh crore, Grand Total {grand[c]:.3f} ({sid} {period})")
    return rows


class BudgetDemands(Source):
    name = "budget_demands"
    panel = True
    series_ids = tuple(STAGES.values())

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL, suffix=".xlsx")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        out = pd.DataFrame(parse_statement(raws[0].content))
        out["note"] = "Demand No. " + out.pop("demand").astype(str)
        return out


SOURCE = BudgetDemands()
