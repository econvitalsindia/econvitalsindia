"""Grid-India daily PSP report (data for 27 Oct 2026)."""
from pipelines.sources.gridindia.psp import data_date, fy_of, parse_psp
from tests.conftest import FIXTURES
from datetime import date


def test_parse_psp():
    out = parse_psp((FIXTURES / "gridindia" / "psp_2026-10-27.xls").read_bytes())
    assert out["power_energy_met"] == 4865.17         # MU
    assert out["power_peak_demand"] == 226.226        # GW (226,226 MW)
    assert out["power_solar_gen"] == 623.24
    assert out["power_wind_gen"] == 274.64


def test_helpers():
    assert data_date("27.10.26_NLDC_PSPNEW") == date(2026, 10, 27)
    assert fy_of(date(2026, 3, 31)) == "2025-26" and fy_of(date(2026, 4, 1)) == "2026-27"
