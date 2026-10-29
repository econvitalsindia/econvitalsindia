"""Effective exchange rates of the rupee, monthly, from the BIS data portal.

RBI's own 40-currency REER/NEER sit in its monthly Bulletin, whose tables have no stable
links (the archive form returns unrelated tables). The Bank for International Settlements
publishes comparable indices through a public SDMX API:
    https://stats.bis.org/api/v1/data/WS_EER/M.R+N.B.IN/all?format=csv
key = monthly . Real/Nominal . Broad basket (64 economies) . India. Index, 2020 = 100;
a rise means the rupee has strengthened against the basket. The CSV is long:
EER_TYPE (R/N), TIME_PERIOD (YYYY-MM), OBS_VALUE.

Series: reer_bis_broad, neer_bis_broad.
"""
from __future__ import annotations

import io

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://stats.bis.org/api/v1/data/WS_EER/M.R+N.B.IN/all?format=csv&startPeriod=2005-01"
SERIES = {"R": "reer_bis_broad", "N": "neer_bis_broad"}


class BisEer(Source):
    name = "bis_eer"
    series_ids = tuple(SERIES.values())

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL, suffix=".csv")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        df = pd.read_csv(io.BytesIO(raws[0].content), dtype={"TIME_PERIOD": str})
        df = df[df["EER_BASKET"].eq("B") & df["REF_AREA"].eq("IN") & df["OBS_VALUE"].notna()]
        if df.empty:
            raise ValueError("BIS returned no India broad EER observations")
        return pd.DataFrame({"series_id": df["EER_TYPE"].map(SERIES), "period": df["TIME_PERIOD"] + "-01",
                             "value": df["OBS_VALUE"].astype(float), "note": "BIS, broad basket, 2020 = 100"})


SOURCE = BisEer()
