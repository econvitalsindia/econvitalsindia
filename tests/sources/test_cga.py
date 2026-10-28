"""CGA 'Accounts at a Glance': monthly layout and the March (provisional, vs RE) layout."""
from pipelines.sources.cga.monthly_accounts import SOURCE, fy_code, number
import pandas as pd


def at(df, sid, period):
    return df[(df.series_id == sid) & (df.period == period)]


def test_monthly_and_march(raw_from):
    df = SOURCE.parse([raw_from("cga/glance_2026-08.htm"), raw_from("cga/glance_2025-03_provisional.htm")])
    aug = at(df, "cga_fiscal_deficit_fytd", "2026-08-01")
    assert aug.value.item() == 7.1025                                    # ₹ 7,10,249 crore
    assert at(df, "cga_fiscal_deficit_pct_be", "2026-08-01").value.item() == 41.9
    assert at(df, "cga_fiscal_deficit_pct_be_prev", "2026-08-01").value.item() == 38.1
    mar = at(df, "cga_fiscal_deficit_fytd", "2025-03-01")
    assert len(mar) == 1 and "Revised Estimates" in mar.note.item()


def test_helpers():
    assert fy_code(pd.Period("2026-08", freq="M")) == "2627"
    assert fy_code(pd.Period("2026-02", freq="M")) == "2526"
    assert number("3 087960") == 3087960
