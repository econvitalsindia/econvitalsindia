"""RBI home page snapshot parser, pinned to the page as read on 2026-10-28."""
from pipelines.sources.rbi.home_rates import SOURCE


def test_parse_snapshot(raw_from):
    df = SOURCE.parse([raw_from("rbi/home_rates/2026-10-28.html")]).set_index("series_id")
    assert df.loc["repo_rate", "value"] == 5.50 and df.loc["repo_rate", "period"] == "2026-10-28"
    assert df.loc["sdf_rate", "value"] == 5.25
    assert df.loc["msf_rate", "value"] == 5.75
    assert df.loc["crr", "value"] == 3.00 and df.loc["slr", "value"] == 18.00
    assert df.loc["usdinr_ref", "value"] == 95.2278 and df.loc["usdinr_ref", "period"] == "2026-10-28"
    assert df.loc["gsec_10y_yield", "value"] == 7.4533
    assert df.loc["gsec_10y_yield", "period"] == "2026-10-27"
    assert "6.94% GS 2036" in df.loc["gsec_10y_yield", "note"]
    assert df.loc["tbill_91d", "value"] == 5.9337
    assert df.loc["sensex_close", "value"] == 73598.67
    assert df.loc["nifty50_close", "value"] == 22749.75
    assert len(df) == len(SOURCE.series_ids)
