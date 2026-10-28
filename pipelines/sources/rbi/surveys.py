"""RBI forward-looking surveys released with each MPC decision: consumer confidence
(urban UCCS, rural RCCS) and the Survey of Professional Forecasters (SPF).

Found like the IESH (pipelines/sources/rbi/iesh.py): the "results of Forward Looking
Surveys" press release links each survey's publication page and PDF.
- UCCS / RCCS: the "Consumer Confidence Index" row of the net-responses summary gives the
  Current Situation Index and Future Expectations Index for the last two rounds
  (index = 100 + average net response; above 100 = optimism).
- SPF: Annex 1 (current financial year) and Annex 2 (next year) give median forecasts.
  Period = month of the results release; the note says which financial year is forecast.
Newest release wins for periods printed twice.
"""
from __future__ import annotations

import io
import re

import pandas as pd
import pdfplumber

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series
from pipelines.sources.rbi._press import RELEASE, releases, survey_pdfs

BACKFILL_MONTHS, RECENT_MONTHS, MIN_HISTORY = 14, 3, 4
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
CONFIDENCE = {"UCCS": ("uccs_csi", "uccs_fei"), "RCCS": ("rccs_csi", "rccs_fei")}
# SPF Annex row label start -> series stem; median is the 2nd of 6 numbers.
SPF_ROWS = {"GDP at constant prices": "spf_gdp", "Inflation based on CPI Combined": "spf_cpi",
            "Inflation based on Core": "spf_core_cpi", "Fiscal Deficit of Central Govt": "spf_fiscal_deficit"}


def pdf_text(content: bytes) -> str:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def round_period(label: str) -> str:
    """'Sep-26' -> '2026-09-01'."""
    mon, yy = label.split("-")
    return f"20{yy}-{MONTHS.index(mon) + 1:02d}-01"


def parse_confidence(text: str, kind: str) -> list[dict]:
    head = re.search(r"Current Perceptions One year ahead Expectations\s+(\w{3}-\d{2}) (\w{3}-\d{2})", text)
    row = re.search(r"Consumer Confidence\s+([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)\s+Index", text)
    if not (head and row):
        raise ValueError(f"{kind}: confidence index row not found")
    prev, cur = round_period(head.group(1)), round_period(head.group(2))
    csi, fei = CONFIDENCE[kind]
    v = [float(x) for x in row.groups()]
    return [{"series_id": csi, "period": prev, "value": v[0]}, {"series_id": csi, "period": cur, "value": v[1]},
            {"series_id": fei, "period": prev, "value": v[2]}, {"series_id": fei, "period": cur, "value": v[3]}]


def parse_spf(text: str, period: str) -> list[dict]:
    rows = []
    for annex, horizon in (("Annex 1: Annual Forecasts for", "cur"), ("Annex 2: Annual Forecasts for", "next")):
        start = text.find(annex)
        if start < 0:
            raise ValueError(f"SPF {annex!r} not found")
        fy = re.match(r"[^\d]*(\d{4}-\d{2})", text[start + len(annex) - 4:start + len(annex) + 12]).group(1)
        block = text[start:text.find("Annex", start + 10)]
        for label, stem in SPF_ROWS.items():
            # The six statistics (mean, median, max, min, quartiles) follow the label either
            # on the same line or on the next one, depending on the round's layout.
            m = re.search(re.escape(label) + r"[^\d\n]*(?:\n[^\d\n]*)?" + r"\s+".join([r"(-?\d+\.\d+)"] * 6), block)
            if m:
                rows.append({"series_id": f"{stem}_{horizon}_fy", "period": period, "value": float(m.group(2)),
                             "note": f"median forecast for {fy}"})
    if not rows:
        raise ValueError("no SPF forecasts parsed")
    return rows


class RbiSurveys(Source):
    name = "rbi_surveys"
    series_ids = ("uccs_csi", "uccs_fei", "rccs_csi", "rccs_fei",
                  *(f"{s}_{h}_fy" for s in SPF_ROWS.values() for h in ("cur", "next")))

    def fetch(self) -> list[Raw]:
        months = BACKFILL_MONTHS if len(load_series("uccs_csi")) < MIN_HISTORY else RECENT_MONTHS
        found = releases(lambda t: "results of Forward Looking Surveys" in t, months)
        raws = []
        for prid in sorted(found, key=int, reverse=True):
            date = re.search(r"Date : (\w{3}) \d+, (\d{4})", get(RELEASE.format(prid=prid)).text.replace("&nbsp;", " "))
            stamp = f"#{date.group(2)}-{MONTHS.index(date.group(1)) + 1:02d}-01" if date else ""
            for kind, url in survey_pdfs(prid).items():
                if kind in ("UCCS", "RCCS") or kind.startswith("SPF"):
                    raw = fetch_raw(url, suffix=".pdf")
                    raw.url = f"{raw.url}#{kind}{stamp}"
                    raws.append(raw)
        if not raws:
            raise RuntimeError("no forward-looking survey PDFs found")
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            tag = raw.url.split("#")[1]
            text = pdf_text(raw.content)
            try:
                if tag in CONFIDENCE:
                    rows += parse_confidence(text, tag)
                elif tag.startswith("SPF") and raw.url.count("#") >= 2:
                    rows += parse_spf(text, raw.url.split("#")[2])
            except ValueError as e:
                # Older survey PDFs can use another layout: skip loudly, keep the rest.
                print(f"  surveys: skipped {raw.url.split('#')[0]} ({tag}): {e}")
        df = pd.DataFrame(rows)
        df["note"] = df.get("note", pd.Series(dtype=str)).fillna("RBI survey")
        return df.drop_duplicates(subset=["series_id", "period"], keep="first")


SOURCE = RbiSurveys()
