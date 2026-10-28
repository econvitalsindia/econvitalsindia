"""CPI excluding food and fuel ("core"), and the RBI-definition "fuel" index. Original measures.

Computed from stored MoSPI component indices (pipelines/sources/mospi/cpi.py) with the
weights in registry/weights/cpi2024_core.yaml. Because CPI 2024 is a fixed-weight index,
the general index is the weighted sum of its parts, so

    core = (100 * general - w_food * food - w_elec * elec_gas_fuels - w_veh * vehicle_fuels) / w_core
    fuel = (w_elec * elec_gas_fuels + w_veh * vehicle_fuels) / (w_elec + w_veh)

Method and validation against RBI's published core: docs/guidebook/08-original-measures.md.
Runs after its inputs (derived sources run last).
"""
from __future__ import annotations

import pandas as pd
import yaml

from pipelines.core import Raw, Source
from pipelines.core.store import ROOT, load_series

WEIGHTS = ROOT / "registry" / "weights" / "cpi2024_core.yaml"
INPUTS = {"general": "cpi_headline_index", "food": "cpi_food_bev_index",
          "elec": "cpi_elec_gas_fuels_index", "veh": "cpi_vehicle_fuels_index"}


def compute(indices: pd.DataFrame, w: dict) -> pd.DataFrame:
    """indices: columns general, food, elec, veh indexed by period -> core and fuel indices."""
    df = indices.dropna()
    fuel_w = w["electricity_gas_fuels"] + w["vehicle_fuels"]
    core = (100 * df.general - w["food_and_beverages"] * df.food
            - w["electricity_gas_fuels"] * df.elec - w["vehicle_fuels"] * df.veh) / w["core"]
    fuel = (w["electricity_gas_fuels"] * df.elec + w["vehicle_fuels"] * df.veh) / fuel_w
    return pd.concat([
        pd.DataFrame({"series_id": "cpi_core_index", "period": df.index, "value": core.round(2).values}),
        pd.DataFrame({"series_id": "cpi_fuel_index", "period": df.index, "value": fuel.round(2).values}),
    ], ignore_index=True)


class CoreCPI(Source):
    name = "derived_core_cpi"
    derived = True
    series_ids = ("cpi_core_index", "cpi_fuel_index")

    def fetch(self) -> list[Raw]:
        return []

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        w = yaml.safe_load(WEIGHTS.read_text())
        assert abs(w["food_and_beverages"] + w["core"] + w["electricity_gas_fuels"]
                   + w["vehicle_fuels"] - 100) < 0.01, "core CPI weights must sum to 100"
        indices = pd.concat({k: load_series(sid).set_index("period")["value"].astype(float)
                             for k, sid in INPUTS.items()}, axis=1)
        out = compute(indices, w)
        out["note"] = "site calculation (Original); weights in registry/weights/cpi2024_core.yaml"
        return out


SOURCE = CoreCPI()
