"""FBIL par yield curve, NSDL FPI flows and AMFI mutual fund flows, pinned to real files."""
from pipelines.sources.amfi.monthly import parse_report
from pipelines.sources.fbil.gsec_curve import TENORS, parse_par_yield
from pipelines.sources.nsdl.fpi import parse_year


def fixture(raw_from, rel):
    return raw_from(rel).content


def test_par_yield_curve(raw_from):
    rows = {r["entity"]: r["value"] for r in parse_par_yield(fixture(raw_from, "fbil/gsec_2026-10-22.xlsx"))}
    assert set(rows) == set(TENORS.values())
    assert rows["1y"] == 6.45 and rows["10y"] == 7.5 and rows["40y"] == 7.91      # semi-annual column
    assert {r["period"] for r in parse_par_yield(fixture(raw_from, "fbil/gsec_2026-10-22.xlsx"))} == {"2026-10-22"}


def test_fpi_columns_change_over_years(raw_from):
    def get(year, sid, period):
        rows = parse_year(fixture(raw_from, f"nsdl/fpi_{year}.html"))
        return next(r["value"] for r in rows if r["series_id"] == sid and r["period"] == period)
    # 2026: debt = general limit + VRR + FAR (-7308 + 60 + 13261); mutual funds' debt excluded.
    assert get(2026, "fpi_debt_net", "2026-01-01") == 6013
    assert get(2026, "fpi_equity_net", "2026-01-01") == -35962
    assert get(2026, "fpi_total_net", "2026-10-01") == -24351                  # "October **", to date
    assert get(2023, "fpi_debt_net", "2023-01-01") == 3531 - 1076               # Debt + Debt-VRR
    assert get(2019, "fpi_total_net", "2019-01-01") == -5556


def test_amfi_monthly(raw_from):
    rows = {r["series_id"]: r["value"] for r in parse_report(fixture(raw_from, "amfi/amsep2026repo.xls"))}
    assert rows == {"mf_net_inflow_debt": -183155.76, "mf_net_inflow_equity": 38306.55,
                    "mf_net_inflow_total": -133375.57, "mf_aum_total": 82.6412}
    # Older layout: line breaks in headers, "AUM as on".
    old = {r["series_id"]: (r["period"], r["value"]) for r in parse_report(fixture(raw_from, "amfi/ammay2019repo.xls"))}
    assert old["mf_net_inflow_equity"] == ("2019-05-01", 5407.75)
