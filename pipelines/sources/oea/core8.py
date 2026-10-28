"""Index of Core Industries (base 2022-23), monthly, from OEA's download file.

File: eaindustry.nic.in/eight_core_infra/Core_Industries_2022_23_<yyyymmdd>.xlsx,
linked from ici_download_data.asp. Sheet "Index": one row per month ("Apr-23"),
followed by annual rows that are skipped. The 2022-23 base adds iron ore to the
eight traditional core industries.
"""
from __future__ import annotations

import io

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.sources.oea._site import find_link, month_label

COLUMNS = {
    "Overall Index": "core_overall_index", "Coal": "core_coal_index",
    "Natural Gas": "core_natural_gas_index", "Crude Oil": "core_crude_oil_index",
    "Refinery Products": "core_refinery_index", "Fertilizers": "core_fertilizers_index",
    "Steel": "core_steel_index", "Cement": "core_cement_index",
    "Electricity": "core_electricity_index", "Iron Ore": "core_iron_ore_index",
}


class OeaCoreIndustries(Source):
    name = "oea_core_industries"
    series_ids = tuple(COLUMNS.values())

    def fetch(self) -> list[Raw]:
        url = find_link("ici_download_data.asp", r"eight_core_infra/Core_Industries_2022_23_\d{8}\.xlsx")
        return [fetch_raw(url, suffix=".xlsx")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        df = pd.read_excel(io.BytesIO(raws[0].content), sheet_name="Index", header=None)
        header_row = df.index[df[0].astype(str).str.strip() == "Months/Years"][0]
        names = {i: str(v).strip() for i, v in df.iloc[header_row].items()}
        missing = set(COLUMNS) - set(names.values())
        if missing:
            raise ValueError(f"core industries columns missing: {sorted(missing)}")
        out = []
        for _, row in df.iloc[header_row + 1:].iterrows():
            period = month_label(row[0])
            if period is None:
                continue  # annual and FYTD rows
            out += [{"series_id": COLUMNS[names[i]], "period": period, "value": float(row[i])}
                    for i in names if names[i] in COLUMNS and pd.notna(row[i])]
        return pd.DataFrame(out)


SOURCE = OeaCoreIndustries()
