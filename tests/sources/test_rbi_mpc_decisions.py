"""MPC decisions from the minutes' resolution: rate, stance and size splits."""
from pipelines.sources.rbi.mpc_decisions import decision, size_split
from pipelines.sources.rbi.mpc_minutes import text_of


def text(raw_from, month):
    return text_of(raw_from(f"rbi/mpc_minutes_{month}.html").content)


def test_cut_reads_new_rate_not_old(raw_from):
    # "by 25 basis points from 6.5 per cent to 6.25 per cent"
    assert decision(text(raw_from, "2016-10")) == (6.25, "accommodative")


def test_hold_and_stance_in_resolution(raw_from):
    assert decision(text(raw_from, "2017-06")) == (6.25, "neutral")
    # "remain focused on withdrawal of accommodation"
    assert decision(text(raw_from, "2022-06")) == (4.9, "withdrawal of accommodation")


def test_stance_after_outlook_and_size_split(raw_from):
    # 2025 minutes: "voted to reduce ... by 50 basis points (bps) to 5.50 per cent"; the stance
    # change comes later ("change the stance from accommodative to neutral").
    t = text(raw_from, "2025-06")
    assert decision(t) == (5.5, "neutral")
    assert size_split(t) == "1 member voted for 25 bp"
    assert size_split(text(raw_from, "2025-02")) == ""
