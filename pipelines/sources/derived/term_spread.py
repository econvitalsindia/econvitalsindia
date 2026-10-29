"""Term spread: the 10-year government bond par yield (FBIL curve) minus the policy repo rate.

The repo rate in force on each date is the last stored value on or before it (it changes
only at MPC meetings). Also republishes the curve's 10-year point as a plain daily series,
so charts and tables can use it like any other series. Site calculation.
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_panel, load_series


class TermSpread(Source):
    name = "derived_term_spread"
    derived = True
    series_ids = ("gsec_par_10y", "term_spread_10y_repo")

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        curve = load_panel("gsec_par_yield")
        ten = curve[curve["entity"] == "10y"][["period", "value"]].astype({"value": float}).sort_values("period")
        repo = load_series("repo_rate")[["period", "value"]].astype({"value": float}).sort_values("period")
        both = pd.merge_asof(ten.assign(d=pd.to_datetime(ten["period"])),
                             repo.assign(d=pd.to_datetime(repo["period"])).rename(columns={"value": "repo"})[["d", "repo"]],
                             on="d", direction="backward").dropna()
        return pd.concat([
            pd.DataFrame({"series_id": "gsec_par_10y", "period": ten["period"], "value": ten["value"],
                          "note": "FBIL par yield curve, 10 years"}),
            pd.DataFrame({"series_id": "term_spread_10y_repo", "period": both["period"],
                          "value": (both["value"] - both["repo"]).round(2),
                          "note": "site calculation: 10-year par yield minus repo rate in force"}),
        ])


SOURCE = TermSpread()
