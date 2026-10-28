"""PPAC products-wise consumption, FY 2026-27 (published 06.10.2026)."""
from datetime import datetime, timezone

from pipelines.core import Raw
from pipelines.sources.ppac.consumption import SOURCE
from tests.conftest import FIXTURES


def test_parse_consumption():
    body = (FIXTURES / "ppac" / "consumption_fy2026.json").read_bytes()
    df = SOURCE.parse([Raw(body, "fixture", datetime.now(timezone.utc), "x", ".json")])
    got = df.set_index(["series_id", "period"])["value"]
    assert got[("fuel_consumption_total", "2026-09-01")] == 19259.0   # title wrapped in <b> tags
    assert got[("diesel_consumption", "2026-09-01")] == 7164.0
    assert got[("lpg_consumption", "2026-09-01")] == 2544.0
    assert ("petrol_consumption", "2026-10-01") not in got.index      # future months are blank
    assert set(df["series_id"]) == set(SOURCE.series_ids)
