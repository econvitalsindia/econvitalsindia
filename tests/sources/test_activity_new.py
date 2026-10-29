"""UPI (RBI PSI), e-way bills (GST portal) and air traffic (AAI), pinned to real files."""
from pipelines.sources.aai.traffic import SOURCE as AAI
from pipelines.sources.gst.ewaybills import SOURCE as EWB
from pipelines.sources.rbi.payments import SOURCE as PSI


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)].value.item()


def test_upi_from_psi(raw_from):
    df = PSI.parse([raw_from("rbi/psi_2026-09.xlsx")])
    assert at(df, "upi_volume", "2026-09-01") == 2406.838          # 240,683.80 lakh -> crore
    assert at(df, "upi_value", "2026-09-01") == 29.374             # Rs crore -> lakh crore
    assert at(df, "upi_volume", "2025-09-01") == 1963.3433         # year-earlier column
    assert at(df, "upi_volume", "2026-08-01") == 2450.8958         # previous-month column
    assert len(df) == 6                                            # FY-to-date column skipped


def test_ewaybills_sum_within_and_outgoing(raw_from):
    df = EWB.parse([raw_from("gst/ewb-data-2026-27.xlsx")])
    # Aug 2026: within 90,300,765 + outgoing 46,982,311 = 13.73 crore
    assert at(df, "ewaybills_count", "2026-08-01") == 13.7283
    assert sorted(df.period.unique())[0] == "2026-04-01"
    old = EWB.parse([raw_from("gst/ewb-data-2018-19.xlsx")])        # older header layout
    assert sorted(old.period.unique())[0] == "2018-07-01"
    assert at(old, "ewaybills_count", "2019-03-01") == 5.3426


def test_aai_month_and_year_earlier(raw_from):
    df = AAI.parse([raw_from("aai/TRSep2k_26.pdf")])
    assert at(df, "air_passengers_domestic", "2026-09-01") == 24.0
    assert at(df, "air_passengers_domestic", "2025-09-01") == 25.61
    assert at(df, "air_passengers_international", "2026-09-01") == 6.1
    assert at(df, "air_freight_total", "2026-09-01") == 372.27      # month, not April-to-date


def test_aai_split_digits(raw_from):
    # This PDF prints "5 . 56" and "2 2 0 .70"; the % change on the line is the check.
    df = AAI.parse([raw_from("aai/TRApr2k26.pdf")])
    assert at(df, "air_passengers_international", "2026-04-01") == 5.56
    assert at(df, "air_freight_total", "2026-04-01") == 347.56
