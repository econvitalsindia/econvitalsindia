"""ECB registrations: the grand total under each of RBI's layouts, in Indian digit grouping."""
from pipelines.sources.rbi.ecb import parse_page


def test_layouts(raw_from):
    got = {f: parse_page(raw_from(f"rbi/ecb/{f}.html").content) for f in ("2026-aug", "2026-feb", "2024-may")}
    assert got["2026-aug"] == {"series_id": "ecb_registrations", "period": "2026-08-01", "value": 8.129}  # General + Special
    assert got["2026-feb"]["period"] == "2026-02-01" and got["2026-feb"]["value"] == 4.596                 # Automatic+Approval
    assert got["2024-may"]["value"] == 4.012                                                                # bare "Total"
