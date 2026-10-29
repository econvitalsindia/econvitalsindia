"""Peers: BIS policy rates and CPI, World Bank GDP growth."""
from pipelines.sources.intl.peers import SOURCE


def test_peers(raw_from):
    df = SOURCE.parse([raw_from("intl/bis_policy.csv"), raw_from("intl/bis_cpi.csv"), raw_from("intl/wb_gdp.json")])
    at = lambda sid, e, p: df[(df.series_id == sid) & (df.entity == e) & (df.period == p)].value.item()
    assert at("peer_policy_rate", "India", "2026-09-01") == 5.25
    assert at("peer_cpi_inflation", "China", "2026-09-01") == 0.9
    assert df[df.series_id == "peer_gdp_growth"].entity.nunique() == 9
    assert not df.duplicated(["series_id", "entity", "period"]).any()
