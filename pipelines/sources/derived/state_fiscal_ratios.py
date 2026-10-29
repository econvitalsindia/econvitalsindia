"""State fiscal ratios, % of GSDP: gross fiscal deficit, outstanding liabilities, interest.

Site calculation from the RBI Handbook panels (rbi/state_finances.py): value / GSDP at
current prices of the same state and financial year (liabilities: end-March of that year).
GSDP is on the 2011-12 base, as printed in the Handbook, so ratios can differ from those in
RBI's State Finances report, which may use newer GSDP. The note keeps the fiscal figure's
stage (Accounts / Revised / Budget Estimates).
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_panel

RATIOS = {"state_gfd": "state_gfd_pct_gsdp", "state_liabilities": "state_debt_pct_gsdp",
          "state_interest": "state_interest_pct_gsdp"}


class StateFiscalRatios(Source):
    name = "derived_state_fiscal_ratios"
    derived = True
    panel = True
    series_ids = tuple(RATIOS.values())

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        gsdp = load_panel("state_gsdp_current").astype({"value": float}).set_index(["entity", "period"])["value"]
        out = []
        for src, sid in RATIOS.items():
            df = load_panel(src).astype({"value": float})
            df["gsdp"] = df.set_index(["entity", "period"]).index.map(gsdp)
            df = df.dropna(subset=["gsdp"])
            df = df[df["gsdp"] > 0]
            out.append(pd.DataFrame({"series_id": sid, "entity": df["entity"], "period": df["period"],
                                     "value": (100 * df["value"] / df["gsdp"]).round(2), "note": df["note"]}))
        return pd.concat(out)


SOURCE = StateFiscalRatios()
