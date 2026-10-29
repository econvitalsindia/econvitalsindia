"""Budget at a Glance (Budget 2026-27)."""
from pipelines.sources.budget.glance import ORDER, SOURCE


def at(df, sid, entity, period):
    return df[(df.series_id == sid) & (df.entity == entity) & (df.period == period)].value.item()


def test_budget_at_a_glance(raw_from):
    df = SOURCE.parse([raw_from("budget/budget_at_a_glance_2026-27.xlsx")])
    assert at(df, "budget_be", "Fiscal deficit", "2026-04-01") == 16.9577        # Rs 16,95,768 crore
    assert at(df, "budget_re", "Fiscal deficit", "2025-04-01") == 15.5849
    assert at(df, "budget_actuals", "Fiscal deficit", "2024-04-01") == 15.7443
    assert at(df, "budget_be", "Fiscal deficit, % of GDP", "2026-04-01") == 4.3  # "(4.3)" on the row below
    assert at(df, "budget_actuals", "Revenue deficit, % of GDP", "2024-04-01") == 1.7
    # "Revenue Deficit" must not pick up "Effective Revenue Deficit".
    assert at(df, "budget_be", "Revenue deficit", "2026-04-01") == 5.9234
    assert set(df.entity) == set(ORDER)
    assert len(df) == len(ORDER) * 4
