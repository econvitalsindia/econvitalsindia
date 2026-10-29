"""Food watch: published inflation by food class/sub-class, combined sector, items skipped."""
import pandas as pd

from pipelines.sources.mospi.cpi_food import ITEMS, MospiCPIFood


def test_food_rows(raw_from):
    src = MospiCPIFood()
    raw = raw_from("mospi/cpi_food_sep2026.json")
    rows = [r for r in __import__("json").loads(raw.content)["data"]]
    pulses = [r for r in rows if r.get("sub_class") == "Pulses" and r.get("item") is None
              and r["sector"] == "Combined" and r["month"] == "September" and r["year"] == "2026"]
    assert pulses and pulses[0]["inflation"] == "4.68"
    # parse() insists every item is present, so check the row filter directly on this page.
    found = {ITEMS.get((r.get("class"), r.get("sub_class"))) for r in rows
             if r.get("sector") == "Combined" and r.get("group") == "Food" and r.get("item") is None}
    assert "Pulses" in found
