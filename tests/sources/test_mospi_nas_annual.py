"""Annual national accounts with the estimate stage in the note."""
from pipelines.sources.mospi.nas_annual import SOURCE
from pipelines.sources.mospi.nas_annual_sectors import SOURCE as SECTORS


def test_annual_growth_and_stage(raw_from):
    raws = [raw_from("mospi/nas_annual_gdp.json"), raw_from("mospi/nas_annual_gva.json")]
    df = SOURCE.parse(raws).set_index(["series_id", "period"])
    assert df.loc[("gdp_real_growth_fy", "2025-04-01"), "value"] == 7.8                # constant prices
    assert df.loc[("gdp_nominal_growth_fy", "2025-04-01"), "value"] == 8.6             # current prices
    assert df.loc[("gdp_real_growth_fy", "2023-04-01"), "note"] == "Final Estimates"
    assert df.loc[("gva_real_growth_fy", "2025-04-01"), "value"] == 7.9                # "Total Gross Value Added"
    sec = SECTORS.parse(raws)
    assert sec["entity"].nunique() == 8 and not sec.duplicated(["entity", "period"]).any()   # sub-industries skipped
