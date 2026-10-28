"""RBI Inflation Expectations Survey of Households (bi-monthly, released on MPC days).

Path: press release "RBI releases the results of Forward Looking Surveys" (found via the
press-release index) -> its PublicationsView links -> the IESH PDF. Table 3 gives, for
the last seven rounds, mean and median (with standard errors) of current inflation
perception and of expectations three months and one year ahead. We keep the medians.
The newest release wins for any round printed more than once.
"""
from __future__ import annotations

import io
import re

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series
from pipelines.sources.rbi._press import RELEASE, releases

BACKFILL_MONTHS, RECENT_MONTHS, MIN_HISTORY = 14, 3, 6
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
# Column positions of the medians among the 12 numbers on each Table 3 row.
MEDIANS = {"iesh_current_perception": 2, "iesh_3m_ahead": 6, "iesh_1y_ahead": 10}


def parse_table3(text: str) -> list[dict]:
    start = text.find("Table 3: Household Inflation Expectations")
    if start < 0:
        raise ValueError("IESH Table 3 not found")
    block = text[start:text.find("Table 4", start)]
    rows = []
    for m in re.finditer(r"^(" + "|".join(MONTHS) + r")-(\d{2})((?:\s+-?\d+\.\d+){12})", block, re.M):
        period = f"20{m.group(2)}-{MONTHS.index(m.group(1)) + 1:02d}-01"
        nums = [float(x) for x in m.group(3).split()]
        rows += [{"series_id": sid, "period": period, "value": nums[i]} for sid, i in MEDIANS.items()]
    if not rows:
        raise ValueError("no survey rounds parsed from IESH Table 3")
    return rows


class RbiIESH(Source):
    name = "rbi_iesh"
    series_ids = tuple(MEDIANS)

    def fetch(self) -> list[Raw]:
        months = BACKFILL_MONTHS if len(load_series("iesh_1y_ahead")) < MIN_HISTORY else RECENT_MONTHS
        found = releases(lambda t: "results of Forward Looking Surveys" in t, months)
        raws = []
        for prid in sorted(found, key=int, reverse=True):  # newest first
            page = get(RELEASE.format(prid=prid)).text
            for pub in dict.fromkeys(re.findall(r"PublicationsView\.aspx\?id=(\d+)", page)):
                pub_page = get(f"https://www.rbi.org.in/Scripts/PublicationsView.aspx?id={pub}").text
                pdf = re.search(r"https://rbidocs\.rbi\.org\.in/rdocs/Publications/PDFs/IESH[^\"']+\.PDF", pub_page, re.I)
                if pdf:
                    raws.append(fetch_raw(pdf.group(0), suffix=".pdf"))
                    break
        if not raws:
            raise RuntimeError("no IESH results found")
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            with pdfplumber.open(io.BytesIO(raw.content)) as pdf:
                rows += parse_table3("\n".join(p.extract_text() or "" for p in pdf.pages))
        df = pd.DataFrame(rows).drop_duplicates(subset=["series_id", "period"], keep="first")
        df["note"] = "median, RBI IESH Table 3"
        return df


SOURCE = RbiIESH()
