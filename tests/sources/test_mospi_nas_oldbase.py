"""Old-base (2011-12) quarterly GDP growth, kept for the base-year bridge."""
from pipelines.sources.mospi.nas_oldbase import SOURCE


def test_old_base(raw_from):
    df = SOURCE.parse([raw_from("mospi/nas_oldbase_page1.json")])
    assert not df.empty and set(df.series_id) == {"gdp_real_growth_2011base"}
    assert df.period.is_unique and df.period.str.match(r"\d{4}-(01|04|07|10)-01").all()
