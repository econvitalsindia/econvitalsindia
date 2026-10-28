"""Recover the weights of CPI 'fuel' components from MoSPI's own indices.

MoSPI publishes division weights but (in machine-readable form) not the weights of
group 04.5 (electricity, gas and other fuels) or class 07.2.2 (fuels and lubricants
for personal transport equipment). CPI 2024 is a fixed-weight (Laspeyres) index, so
each parent index is an exact weighted average of its children:

    I_parent(t) = sum_k s_k * I_k(t),   sum_k s_k = 1

With 20+ months of published indices, constrained least squares recovers the shares
s_k to rounding precision. Fuel weights are then division weight x share.

    uv run python scripts/estimate_core_cpi_weights.py   # prints yaml for registry/weights/
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipelines.core.http import get  # noqa: E402  (handles MoSPI's legacy TLS)

URL = "https://api.mospi.gov.in/api/cpi/getCPIData"
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}
# Division weights, all-India combined, from MoSPI's CPI 2024 press releases.
DIVISION_WEIGHT = {4: 17.66, 7: 8.80}


def pull(division: int) -> pd.DataFrame:
    """All combined all-India rows of one division."""
    rows, page = [], 1
    while True:
        body = json.loads(get(URL, params={
            "base_year": "2024", "series": "Current", "state_code": "1", "sector_code": "3",
            "division_code": str(division), "limit": 100, "page": page, "Format": "JSON"}).content)
        rows += body["data"]
        if page >= body["meta_data"]["totalPages"]:
            df = pd.DataFrame(rows)
            df["t"] = df["year"].astype(int) * 100 + df["month"].map(MONTHS)
            df["index"] = df["index"].astype(float)
            return df
        page += 1


def shares(parent: pd.Series, children: pd.DataFrame) -> tuple[dict, float]:
    """Constrained least squares (shares sum to 1); returns shares and max abs residual."""
    X = children.loc[parent.index].values
    Xd = X[:, :-1] - X[:, [-1]]
    b, *_ = np.linalg.lstsq(Xd, parent.values - X[:, -1], rcond=None)
    s = np.append(b, 1 - b.sum())
    return dict(zip(children.columns, s)), float(np.abs(X @ s - parent.values).max())


def main() -> None:
    d4, d7 = pull(4), pull(7)
    top4 = d4[d4.group.isna()].set_index("t")["index"]
    g4 = d4[d4.group.notna() & d4["class"].isna()].pivot_table(index="t", columns="group", values="index")
    s4, r4 = shares(top4, g4)

    top7 = d7[d7.group.isna()].set_index("t")["index"]
    g7 = d7[d7.group.notna() & d7["class"].isna()].pivot_table(index="t", columns="group", values="index")
    s7, r7 = shares(top7, g7)
    op = "Operation of personal transport equipment"
    top_op = d7[(d7.group == op) & d7["class"].isna()].set_index("t")["index"]
    c_op = d7[(d7.group == op) & d7["class"].notna() & d7.sub_class.isna()].pivot_table(
        index="t", columns="class", values="index")
    s_op, r_op = shares(top_op, c_op)

    w_elec = DIVISION_WEIGHT[4] * s4["Electricity, gas and other fuels"]
    w_vehicle = DIVISION_WEIGHT[7] * s7[op] * s_op["Fuels and lubricants for personal transport equipment"]
    print(f"# months used: {len(top4)}; max abs residuals: div4 {r4:.4f}, div7 {r7:.4f}, op {r_op:.4f}")
    print(f"electricity_gas_fuels_estimated: {w_elec:.3f}")
    print(f"vehicle_fuels_estimated: {w_vehicle:.3f}")
    print(f"# sum {w_elec + w_vehicle:.3f}")


if __name__ == "__main__":
    main()
