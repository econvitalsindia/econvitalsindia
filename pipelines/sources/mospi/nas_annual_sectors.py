"""Annual real GVA growth by broad sector (panel), from the same MoSPI rows as nas_annual.py."""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi.nas_annual import annual_rows, fetch_annual


class MospiNASAnnualSectors(Source):
    name = "mospi_nas_annual_sectors"
    panel = True
    series_ids = ("gva_sector_growth_fy",)

    def fetch(self) -> list[Raw]:
        return fetch_annual()

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        df = annual_rows(raws)
        return df[df["series_id"] == "gva_sector_growth_fy"]


SOURCE = MospiNASAnnualSectors()
