"""India's external debt, quarterly, from RBI's press releases.

Releases are titled "India's External Debt as at the end of June 2026" and found through the
press-release index (_press.releases). The highlights give two quarters each:
  "At end-June 2026, India's external debt was placed at US$ 778.2 billion, an increase of
   US$ 15.4 billion over its level at end-March 2026"
  "The external debt to GDP ratio moderated to 20.8 per cent at end-June 2026 from 20.9 per
   cent at end-March 2026."
The earlier quarter's level is the latest level minus the change. Periods are the first day
of the quarter whose end the release names (end-June 2026 -> 2026-04-01), as for the BoP.
The newest release wins.

Series: external_debt (US$ billion), external_debt_pct_gdp (per cent).
"""
from __future__ import annotations

import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series
from pipelines.sources.rbi._press import RELEASE, releases
from pipelines.sources.rbi.services_trade import page_text

BACKFILL_MONTHS, RECENT_MONTHS = 40, 4
MONTH = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
LEVEL = re.compile(r"external debt was placed at US\$\s*([\d,.]+) billion, (?:recording )?an? (increase|decrease|decline) of US\$\s*"
                   r"([\d,.]+) billion over its level at end-" + MONTH + r"\s+(\d{4})")
AT_END = re.compile(r"At end-" + MONTH + r"\s+(\d{4}),\s*India.s external debt")
RATIO = re.compile(r"external debt to GDP ratio [a-z ]*?to ([\d.]+) per cent at end-" + MONTH + r"\s+(\d{4}) from ([\d.]+)"
                   r" per cent at end-" + MONTH + r"\s+(\d{4})")


def quarter_of(month: str, year: str) -> str:
    """Quarter ending in `month` -> first day of that quarter ('June', '2026' -> '2026-04-01')."""
    m = datetime.strptime(month, "%B").month
    return f"{year}-{m - 2:02d}-01"


def parse_release(text: str) -> list[dict]:
    end = AT_END.search(text)
    level = LEVEL.search(text)
    if not (end and level):
        raise ValueError("external debt level sentence not found")
    now = float(level.group(1).replace(",", ""))
    change = float(level.group(3).replace(",", "")) * (1 if level.group(2) == "increase" else -1)
    rows = [{"series_id": "external_debt", "period": quarter_of(end.group(1), end.group(2)), "value": now},
            {"series_id": "external_debt", "period": quarter_of(level.group(4), level.group(5)),
             "value": round(now - change, 1)}]
    ratio = RATIO.search(text)
    if ratio:
        rows += [{"series_id": "external_debt_pct_gdp", "period": quarter_of(ratio.group(2), ratio.group(3)),
                  "value": float(ratio.group(1))},
                 {"series_id": "external_debt_pct_gdp", "period": quarter_of(ratio.group(5), ratio.group(6)),
                  "value": float(ratio.group(4))}]
    return rows


class ExternalDebt(Source):
    name = "rbi_external_debt"
    series_ids = ("external_debt", "external_debt_pct_gdp")

    def fetch(self) -> list[Raw]:
        months = BACKFILL_MONTHS if len(load_series("external_debt")) < 4 else RECENT_MONTHS
        found = releases(lambda t: "External Debt as at" in t, months)
        if not found:
            raise RuntimeError(f"no external debt releases in the last {months} months")
        return [fetch_raw(RELEASE.format(prid=p), suffix=".html") for p in sorted(found)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:                      # oldest first, so later releases overwrite
            rows += parse_release(page_text(raw.content))
        out = pd.DataFrame(rows).drop_duplicates(["series_id", "period"], keep="last")
        out["note"] = "RBI external debt release (newest wins)"
        return out


SOURCE = ExternalDebt()
