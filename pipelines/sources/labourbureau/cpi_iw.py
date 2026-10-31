"""Consumer Price Index for Industrial Workers (2016=100), Labour Bureau, monthly.

The Labour Bureau home page links the latest "Press Note CPI- IW for <Month> <Year>" PDF;
there is no archive page, so history is built from each new note. A note gives the
all-India general index for the month and the month before, and y/y inflation for the
month and the same month a year earlier.
"""
from __future__ import annotations

import io
import re

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get

HOME = "https://labourbureau.gov.in/"
MONTHS = ("January February March April May June July August September October "
          "November December").split()


def month_iso(month: str, year: str) -> str:
    return f"{int(year):04d}-{MONTHS.index(month) + 1:02d}-01"


def parse_note(text: str) -> list[dict]:
    head = re.search(r"Industrial Workers \(2016=100\)\s*[–-]\s*(" + "|".join(MONTHS) + r"),?\s*(\d{4})", text)
    if not head:
        raise ValueError("CPI-IW press note heading not found")
    cur = month_iso(head.group(1), head.group(2))
    prev = (pd.Period(cur[:7], freq="M") - 1).strftime("%Y-%m-01")
    ya = (pd.Period(cur[:7], freq="M") - 12).strftime("%Y-%m-01")
    gen = re.search(r"General Index\s+([\d.]+)\s+([\d.]+)", text)
    infl = re.search(r"inflation for the month of [A-Za-z]+,?\s*\d{4} stood at\s*(-?[\d.]+)%\s*as compared to\s*(-?[\d.]+)%", text)
    if not (gen and infl):
        raise ValueError("CPI-IW general index or inflation sentence not found")
    return [{"series_id": "cpi_iw_index", "period": prev, "value": float(gen.group(1))},
            {"series_id": "cpi_iw_index", "period": cur, "value": float(gen.group(2))},
            {"series_id": "cpi_iw_inflation", "period": cur, "value": float(infl.group(1))},
            {"series_id": "cpi_iw_inflation", "period": ya, "value": float(infl.group(2))}]


def press_link(page: str) -> str | None:
    """The English CPI-IW press note: "Press-Release-CPI-IW-August-2026...pdf" until Aug 2026,
    "Press-ReleaseCPIIWSept-2026E...pdf" from Sep 2026."""
    m = re.search(r'href="(https://labourbureau\.gov\.in/uploads/public/notice/Press-?Release-?CPI-?IW[^"]+\.pdf)"', page, re.I)
    return m.group(1) if m else None

class LabourBureauCpiIw(Source):
    name = "labourbureau_cpi_iw"
    series_ids = ("cpi_iw_index", "cpi_iw_inflation")

    def fetch(self) -> list[Raw]:
        link = press_link(get(HOME).text)
        if not link:
            raise RuntimeError("no CPI-IW press note linked on the Labour Bureau home page")
        return [fetch_raw(link, suffix=".pdf")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        with pdfplumber.open(io.BytesIO(raws[0].content)) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        df = pd.DataFrame(parse_note(text))
        df["note"] = "Labour Bureau press note"
        return df


SOURCE = LabourBureauCpiIw()
