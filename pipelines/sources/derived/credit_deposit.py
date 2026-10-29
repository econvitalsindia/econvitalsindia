"""Credit-deposit ratio of scheduled commercial banks: bank credit / aggregate deposits, %,
on each fortnightly reporting date (site calculation from the WSS series)."""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_series


class CreditDeposit(Source):
    name = "derived_credit_deposit"
    derived = True
    series_ids = ("credit_deposit_ratio",)

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        c = load_series("scb_credit").set_index("period")["value"].astype(float)
        d = load_series("scb_deposits").set_index("period")["value"].astype(float)
        both = pd.concat([c, d], axis=1, keys=["c", "d"]).dropna()
        both.index.name = None
        return pd.DataFrame({"series_id": "credit_deposit_ratio", "period": both.index,
                             "value": (100 * both["c"] / both["d"]).round(2),
                             "note": "site calculation: bank credit / aggregate deposits"})


SOURCE = CreditDeposit()
