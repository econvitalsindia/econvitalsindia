"""EPFO net payroll additions, monthly, from EPFO's "Net Payroll Data" reports.

The Data Hub (https://www.epfo.gov.in/data-hub/) links one PDF per report month
(".../uploads/<y>/<m>/<Month>-<YYYY>.pdf"). Page 1 has a table by age band: a row per
financial year, then a row per month of the current year:
    Jul-2025 7343 418406 494539 279840 459147 445085 2104360 1550
(six age bands, the total, establishments remitting for the first time). Every report
restates the current year's months, and estimates are revised for months afterwards, so
the newest report that prints a month wins.

EPFO's site refuses requests from GitHub's US runners: fetch is manual
(`make india-update`). The last report linked (checked 2026-10-29) is for September 2025,
covering up to July 2025.

Series: epfo_net_payroll (lakh members, net of exits and rejoiners).
"""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get

PAGE = "https://www.epfo.gov.in/data-hub/"
ROW = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*-(\d{4})((?:\s+-?\d+){8})\s*$", re.M)


def report_date(url: str) -> str:
    m = re.search(r"/([A-Za-z]+)-(\d{4})(?:-\d)?\.pdf$", url)
    return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %Y").strftime("%Y-%m-01")


def parse_report(text: str) -> list[dict]:
    rows = []
    for mon, year, nums in ROW.findall(text):
        values = [int(n) for n in nums.split()]
        rows.append({"period": datetime.strptime(f"{mon} {year}", "%b %Y").strftime("%Y-%m-01"),
                     "value": round(values[6] / 1e5, 4)})
    return rows


class EpfoPayroll(Source):
    name = "epfo_payroll"
    series_ids = ("epfo_net_payroll",)

    def fetch(self) -> list[Raw]:
        page = get(PAGE).text
        links = list(dict.fromkeys(re.findall(r"https://[^\"']+/uploads/\d{4}/\d{2}/[A-Z][a-z]+-\d{4}(?:-\d)?\.pdf", page)))
        if not links:
            raise RuntimeError("no payroll reports linked on the EPFO Data Hub")
        return [fetch_raw(u, suffix=".pdf") for u in links]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            with pdfplumber.open(io.BytesIO(raw.content)) as pdf:
                for r in parse_report(pdf.pages[0].extract_text() or ""):
                    rows.append({**r, "report": report_date(raw.url)})
        df = pd.DataFrame(rows).sort_values("report").drop_duplicates("period", keep="last")
        df["series_id"] = "epfo_net_payroll"
        df["note"] = "provisional; EPFO report of " + df["report"].str[:7]
        return df[["series_id", "period", "value", "note"]].sort_values("period")


SOURCE = EpfoPayroll()
