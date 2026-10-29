"""Air traffic at Indian airports, monthly, from the Airports Authority of India.

The "Traffic News" page (https://www.aai.aero/en/business-opportunities/aai-traffic-news)
links a two-page PDF report per month ("TR<Mon>2k<yy>.pdf"; names vary). Page 1 has a
bilingual table for the month, this year vs the same month last year:
    AIR TRAFFIC REPORT–SEPTEMBER, 2026
    Passengers (in million)
    अंतर्राष्ट्रीय International 6.10 6.37 -4.2
    घरेलू Domestic 24.00 25.61 -6.3
    Freight(in '000 ton) ... कु ल Total 372.27 332.10 12.1
followed by the same table for April-to-date, which is skipped. Only the current calendar
year's reports are linked, so each report's year-earlier column fills the year before.
A month's own report wins over the year-earlier column of the next year's report.

Series: air_passengers_domestic, air_passengers_international (million),
air_freight_total ('000 tonnes).
"""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get

PAGE = "https://www.aai.aero/en/business-opportunities/aai-traffic-news"


def report_month(text: str) -> str:
    # "REPORT–SEPTEMBER, 2026", "REPORT–MAY , 2026", "REPORT – April, 2026"
    m = re.search(r"AIR TRAFFIC REPORT\s*[–-]\s*([A-Za-z]+)\s*,?\s*(\d{4})", text)
    if not m:
        raise ValueError("no 'AIR TRAFFIC REPORT – <MONTH>, <YEAR>' heading")
    return datetime.strptime(f"{m.group(1).title()} {m.group(2)}", "%B %Y").strftime("%Y-%m-01")


def parse_report(text: str) -> list[dict]:
    period = report_month(text)
    prior = f"{int(period[:4]) - 1}{period[4:]}"
    # The month's table ends where the April-to-date table begins ("APRIL - <MONTH>").
    month_table = re.split(r"APRIL\s*[-–]\s*[A-Z]+", text)[0]

    def pair(section: str, line: str) -> tuple[float, float]:
        block = month_table[month_table.index(section):]
        m = re.search(line + r"\s+([^\n]+)", block)
        if not m:
            raise ValueError(f"no '{line}' line under '{section}'")
        # Some PDFs split digits ("5 . 56", "2 2 0 .70"). Drop spaces, then take the two
        # two-decimal values (this year, last year); the rest is the % change, used as a check.
        compact = re.sub(r"[\s,]", "", m.group(1))
        nums = re.match(r"(\d+\.\d\d)(\d+\.\d\d)(-?\d+(?:\.\d+)?)", compact)
        if not nums:
            raise ValueError(f"can't read '{line}' under '{section}': {m.group(1)!r}")
        now, before, pct = (float(x) for x in nums.groups())
        if abs((now / before - 1) * 100 - pct) > 0.3:
            raise ValueError(f"'{line}' under '{section}': {now} vs {before} is not {pct}%")
        return now, before

    rows = []
    for sid, section, line in [("air_passengers_domestic", "Passengers", "Domestic"),
                               ("air_passengers_international", "Passengers", "International"),
                               ("air_freight_total", "Freight", "Total")]:
        now, before = pair(section, line)
        rows.append({"series_id": sid, "period": period, "value": now, "own": True})
        rows.append({"series_id": sid, "period": prior, "value": before, "own": False})
    return rows


class AaiTraffic(Source):
    name = "aai_traffic"
    series_ids = ("air_passengers_domestic", "air_passengers_international", "air_freight_total")

    def fetch(self) -> list[Raw]:
        page = get(PAGE).text
        links = list(dict.fromkeys(re.findall(r"https://www\.aai\.aero/sites/default/files/traffic-news/TR[^\"']+\.pdf", page)))
        if not links:
            raise RuntimeError("no traffic reports linked on the AAI page")
        return [fetch_raw(u, suffix=".pdf") for u in links]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            with pdfplumber.open(io.BytesIO(raw.content)) as pdf:
                rows += parse_report(pdf.pages[0].extract_text() or "")
        df = pd.DataFrame(rows).sort_values("own", ascending=False)
        df = df.drop_duplicates(["series_id", "period"], keep="first")
        df["note"] = df["own"].map({True: "AAI monthly report", False: "AAI, year-earlier column"})
        return df.drop(columns="own")


SOURCE = AaiTraffic()
