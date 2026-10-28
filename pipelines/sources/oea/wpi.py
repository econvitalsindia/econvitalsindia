"""Wholesale Price Index (base 2022-23), all-India, monthly, from OEA's download file.

File: eaindustry.nic.in/indx_download_2223/wpi_monthly_index_<yyyymm>.xlsx, linked
from download_data_2223.asp. One row per commodity (Level, name, 10-digit code,
weight), one column per month from Apr-23. Rows are matched by commodity code.
"""
from __future__ import annotations

import io

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.sources.oea._site import find_link, month_label

CODES = {
    "1000000000": "wpi_headline_index",
    "1100000000": "wpi_primary_index",
    "1101000000": "wpi_food_articles_index",
    "1200000000": "wpi_fuel_power_index",
    "1300000000": "wpi_manufactured_index",
}


class OeaWPI(Source):
    name = "oea_wpi"
    series_ids = tuple(CODES.values())

    def fetch(self) -> list[Raw]:
        url = find_link("download_data_2223.asp", r"indx_download_2223/wpi_monthly_index_\d{6}\.xlsx")
        return [fetch_raw(url, suffix=".xlsx")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        df = pd.read_excel(io.BytesIO(raws[0].content), header=None, dtype={2: str})
        header = df.iloc[0]
        months = {i: month_label(h) for i, h in header.items() if month_label(h)}
        if not months:
            raise ValueError("no month columns found in WPI file (layout changed?)")
        out = []
        for _, row in df.iloc[1:].iterrows():
            sid = CODES.get(str(row[2]).strip().split(".")[0])
            if sid:
                out += [{"series_id": sid, "period": p, "value": float(row[i])}
                        for i, p in months.items() if pd.notna(row[i])]
        return pd.DataFrame(out)


SOURCE = OeaWPI()
