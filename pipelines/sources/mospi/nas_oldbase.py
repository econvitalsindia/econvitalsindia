"""Real GDP growth on the old 2011-12 base, quarterly, kept in full for the base-year bridge.

nas.py publishes growth "as published": the 2011-12 base up to Q4 FY23 and the 2022-23 base
from Q1 FY24. MoSPI also kept publishing the old base for some quarters after that, so the
two overlap (Q1 FY24 to Q2 FY26 when checked on 2026-10-29). This series stores the old base
throughout, so the Methods page can compare the two in the overlap.

Series: gdp_real_growth_2011base (% y/y, constant 2011-12 prices).
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import pages, rows
from pipelines.sources.mospi.nas import OLD, quarter_period


class MospiNASOldBase(Source):
    name = "mospi_nas_oldbase"
    series_ids = ("gdp_real_growth_2011base",)

    def fetch(self) -> list[Raw]:
        return pages("nas/getNASData", {"frequency_code": "Quarterly", "base_year": OLD, "indicator_code": 22})

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        out = [{"series_id": "gdp_real_growth_2011base", "period": quarter_period(r["year"], r["quarter"]),
                "value": float(r["constant_price"]), "note": "base 2011-12"}
               for r in rows(raws) if r.get("constant_price") not in (None, "")]
        if not out:
            raise ValueError("no old-base GDP growth rows")
        return pd.DataFrame(out).drop_duplicates(["period"], keep="last")


SOURCE = MospiNASOldBase()
