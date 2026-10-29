"""Food watch: CPI inflation by food class and key items, all-India combined (base 2024).

Same API as cpi.py (cpi/getCPIData), division 1 (Food and beverages), current series,
combined sector. Records carry MoSPI's published year-on-year "inflation" for every level:
group "Food" -> class (e.g. "Vegetables, tubers, plantains, cooking bananas and pulses")
-> sub_class (e.g. "Pulses"). Published inflation on the 2024 base starts in January 2026
(the current series starts in January 2025).

Panel cpi_food_inflation: entity = a short name for a food class or sub-class (ITEMS),
value = % on a year earlier as published.
"""
from __future__ import annotations

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.sources.mospi._api import pages, rows
from pipelines.sources.mospi.cpi import _float, _period

ENDPOINT = "cpi/getCPIData"
# (class, sub_class) -> short name. sub_class None = the whole class.
ITEMS = {
    ("Cereals and cereal products", None): "Cereals and products",
    ("Cereals and cereal products", "Cereals"): "Cereals (grain)",
    ("Vegetables, tubers, plantains, cooking bananas and pulses", "Pulses"): "Pulses",
    ("Vegetables, tubers, plantains, cooking bananas and pulses", "Fruit-bearing vegetables, fresh or chilled"): "Fruit-bearing vegetables",
    ("Vegetables, tubers, plantains, cooking bananas and pulses", "Leafy or stem vegetables, fresh or chilled"): "Leafy vegetables",
    ("Vegetables, tubers, plantains, cooking bananas and pulses", "Tubers, plantains and cooking bananas, fresh or chilled"): "Tubers",
    ("Vegetables, tubers, plantains, cooking bananas and pulses", "Other vegetables, fresh or chilled"): "Other vegetables",
    ("Oils and fats", "Vegetable oils"): "Vegetable oils",
    ("Milk, other dairy products and eggs", "Milk: liquid"): "Milk",
    ("Milk, other dairy products and eggs", "Eggs"): "Eggs",
    ("Meat, fresh, chilled or frozen", None): "Meat",
    ("Fish and other seafood", None): "Fish and seafood",
    ("Fruits and nuts", None): "Fruits and nuts",
    ("Sugar, confectionery and desserts", "Cane sugar and beet sugar"): "Sugar",
    ("Ready-made food and other food products", "Spices, culinary herbs and seeds"): "Spices",
}


class MospiCPIFood(Source):
    name = "mospi_cpi_food"
    panel = True
    series_ids = ("cpi_food_inflation",)

    def fetch(self) -> list[Raw]:
        return pages(ENDPOINT, {"base_year": "2024", "state_code": "1", "sector_code": "3",
                                "division_code": "1", "series": "Current"})

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        out = []
        for r in rows(raws):
            if r.get("sector") != "Combined" or r.get("group") != "Food" or r.get("item") is not None:
                continue
            name = ITEMS.get((r.get("class"), r.get("sub_class")))
            infl = _float(r.get("inflation"))
            if name and infl is not None:
                out.append({"series_id": "cpi_food_inflation", "entity": name,
                            "period": _period(r["year"], r["month"]), "value": infl, "note": ""})
        df = pd.DataFrame(out).drop_duplicates(["entity", "period"], keep="last")
        missing = set(ITEMS.values()) - set(df["entity"])
        if missing:
            raise ValueError(f"CPI food items not found: {sorted(missing)}")
        return df


SOURCE = MospiCPIFood()
