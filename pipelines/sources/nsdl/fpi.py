"""Net investment by foreign portfolio investors (FPIs), monthly, from NSDL.

Page: https://www.fpi.nsdl.co.in/web/Reports/Yearwise.aspx?RptType=6, "Monthly FPI Net
Investments (Calendar Year - YYYY)" in Rs crore. The year is chosen with an ASP.NET
post-back (field "ddl"). Columns change over the years (nested headers, read with
pandas.read_html):
    2019: Equity | Debt | Hybrid | Total
    2023: Equity | Debt | Debt-VRR | Hybrid | Total
    2026: Equity | Debt (General Limit, VRR, FAR) | Hybrid | Mutual Funds (...) | AIFs | Total
Debt = every debt column directly under FPI investment (not mutual funds' debt schemes).
The current month is marked "October **" and runs to the previous trading day; it is
replaced as the month fills in.

Series (Rs crore a month): fpi_equity_net, fpi_debt_net, fpi_total_net.
"""
from __future__ import annotations

import hashlib
import io
import re
from datetime import date, datetime, timezone

import httpx
import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import HEADERS
from pipelines.core.store import load_series

URL = "https://www.fpi.nsdl.co.in/web/Reports/Yearwise.aspx?RptType=6"
FIRST_YEAR, MIN_HISTORY = 2015, 24
GROUPS = {"Debt", "Mutual Funds", "Hybrid", "Equity", "Total"}


def parse_year(content: bytes) -> list[dict]:
    html = content.decode("utf-8", "ignore")
    year = int(re.search(r"Calendar Year - (\d{4})", html).group(1))
    table = max(pd.read_html(io.StringIO(html)), key=lambda d: d.shape[0] * d.shape[1])
    cols = list(table.columns)
    first = cols[0]

    def kind(col) -> tuple[str, str]:
        leaf, parent = str(col[-1]), str(col[-2])
        return (parent if parent in GROUPS else leaf), leaf

    equity = [c for c in cols if kind(c) == ("Equity", "Equity")]
    debt = [c for c in cols if kind(c)[0].startswith("Debt") and kind(c)[0] != "Mutual Funds"]
    total = [c for c in cols if kind(c)[1] == "Total"]
    if not (equity and debt and total):
        raise ValueError(f"NSDL {year}: equity/debt/total columns not found in {cols}")
    rows = []
    for _, r in table.iterrows():
        month = re.sub(r"[*\s]+$", "", str(r[first]))
        try:
            period = datetime.strptime(f"{month} {year}", "%B %Y").strftime("%Y-%m-01")
        except ValueError:
            continue                                   # "Total - 2026", notes
        def num(c) -> float:
            v = str(r[c]).replace(",", "").strip()
            return 0.0 if v in {"-", "", "nan"} else float(v)        # "-": none that month
        rows += [{"series_id": "fpi_equity_net", "period": period, "value": num(equity[0])},
                 {"series_id": "fpi_debt_net", "period": period, "value": sum(num(c) for c in debt)},
                 {"series_id": "fpi_total_net", "period": period, "value": num(total[0])}]
    return rows


class NsdlFpi(Source):
    name = "nsdl_fpi"
    series_ids = ("fpi_equity_net", "fpi_debt_net", "fpi_total_net")

    def fetch(self) -> list[Raw]:
        this = date.today().year
        first = FIRST_YEAR if len(load_series("fpi_total_net")) < MIN_HISTORY else this - 1
        raws = []
        with httpx.Client(headers=HEADERS, timeout=60, follow_redirects=True) as client:
            page = client.get(URL).text
            for year in range(first, this + 1):
                fields = dict(re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', page))
                fields.update({"__EVENTTARGET": "ddl", "__EVENTARGUMENT": "", "ddl": str(year)})
                # The site occasionally answers a post-back without the table: retry once.
                for _ in range(2):
                    r = client.post(URL, data=fields)
                    r.raise_for_status()
                    if f"Calendar Year - {year}" in r.text:
                        break
                else:
                    raise RuntimeError(f"NSDL returned no table for {year}")
                raws.append(Raw(r.content, f"{URL}&year={year}", datetime.now(timezone.utc),
                                hashlib.sha256(r.content).hexdigest(), ".html"))
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            rows += parse_year(raw.content)
        out = pd.DataFrame(rows)
        out["note"] = "NSDL; current month to date"
        return out


SOURCE = NsdlFpi()
