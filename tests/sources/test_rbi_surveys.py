"""RBI consumer confidence and professional forecasters' surveys."""
from pipelines.sources.rbi.surveys import parse_confidence, parse_spf, pdf_text
from tests.conftest import FIXTURES


def text(name):
    return pdf_text((FIXTURES / "rbi" / "surveys" / name).read_bytes())


def test_uccs():
    rows = {(r["series_id"], r["period"]): r["value"] for r in parse_confidence(text("uccs_2026-09.pdf"), "UCCS")}
    assert rows[("uccs_csi", "2026-09-01")] == 87.9 and rows[("uccs_fei", "2026-07-01")] == 115.3


def test_spf_both_layouts():
    new = {r["series_id"]: r["value"] for r in parse_spf(text("spf_2026-10.pdf"), "2026-10-01")}
    assert new["spf_gdp_cur_fy"] == 7.1 and new["spf_cpi_cur_fy"] == 5.1 and new["spf_gdp_next_fy"] == 7.0
    old = {r["series_id"]: r["value"] for r in parse_spf(text("spf_2026-08_sameline.pdf"), "2026-08-01")}
    assert old["spf_gdp_cur_fy"] == 6.6 and old["spf_cpi_cur_fy"] == 5.0
