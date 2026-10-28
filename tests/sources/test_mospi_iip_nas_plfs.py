"""IIP, national accounts and PLFS parsers, pinned to values MoSPI published (API, 2026-10-28)."""
from pipelines.sources.mospi.iip import SOURCE as IIP
from pipelines.sources.mospi.nas import SOURCE as NAS, quarter_period
from pipelines.sources.mospi.plfs import SOURCE as PLFS


def at(df, sid, period):
    row = df[(df.series_id == sid) & (df.period == period)]
    assert len(row) == 1, (sid, period, len(row))
    return row.iloc[0]


def test_iip(raw_from):
    df = IIP.parse([raw_from("mospi/iip/sample.json")])
    assert at(df, "iip_general_index", "2026-09-01").value == 124.3
    assert at(df, "iip_general_growth", "2026-09-01").value == 6.7
    assert "2022-23" in at(df, "iip_general_growth", "2026-09-01").note
    assert at(df, "iip_capital_goods_index", "2026-09-01").value == 153.4
    assert not df.duplicated(["series_id", "period"]).any()


def test_nas(raw_from):
    df = NAS.parse([raw_from("mospi/nas/sample.json")])
    assert at(df, "gdp_real_growth", "2026-04-01").value == 7.8
    assert at(df, "gdp_nominal_growth", "2026-04-01").value == 10.3
    assert at(df, "gva_real_growth", "2026-04-01").value == 8.2
    assert at(df, "gva_mfg_growth", "2026-04-01").value == 9.2
    assert round(at(df, "gdp_real_level", "2026-04-01").value, 5) == 81.36153  # ₹ lakh crore
    assert not df.duplicated(["series_id", "period"]).any()


def test_quarter_period():
    assert quarter_period("2026-27", "Q1") == "2026-04-01"
    assert quarter_period("2026-27", "Q3") == "2026-10-01"
    assert quarter_period("2025-26", "Q4") == "2026-01-01"


def test_plfs(raw_from):
    df = PLFS.parse([raw_from("mospi/plfs/sample.json")])
    assert at(df, "plfs_ur_monthly", "2026-09-01").value == 5.0
    assert at(df, "plfs_ur_youth_monthly", "2026-09-01").value == 15.2
    assert at(df, "plfs_lfpr_female_monthly", "2026-09-01").value == 34.6
