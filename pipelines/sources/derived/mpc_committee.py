"""MPC Speak, committee level: the average tone of the six members' statements at each
meeting, and the number of members who voted against the rate resolution. Original measure.
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_panel


class MpcCommittee(Source):
    name = "derived_mpc_committee"
    derived = True
    series_ids = ("mpc_committee_tone", "mpc_dissent_count")

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        tone = load_panel("mpc_member_tone").astype({"value": float}).groupby("period")["value"].mean().round(3)
        dissent = load_panel("mpc_member_dissent").astype({"value": float}).groupby("period")["value"].sum()
        return pd.concat([
            pd.DataFrame({"series_id": "mpc_committee_tone", "period": tone.index, "value": tone.values,
                          "note": "site calculation: mean of members' MPC Speak scores"}),
            pd.DataFrame({"series_id": "mpc_dissent_count", "period": dissent.index, "value": dissent.values,
                          "note": "members voting No on the rate resolution"}),
        ])


SOURCE = MpcCommittee()
