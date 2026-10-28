"""CGA monthly trend of tax revenue (statement for August 2026)."""
from pipelines.sources.cga.tax_heads import parse_trend, prefix_of
from tests.conftest import FIXTURES


def test_parse_trend():
    key, out = parse_trend((FIXTURES / "cga" / "DTL3_aug2026.htm").read_text(errors="ignore"))
    assert key == (2026, 4)                                       # FY 2026-27, through August
    assert out[("cga_gross_tax_fytd", "2026-08-01")] == 14.319     # ₹1,431,903 crore
    assert out[("cga_corporate_tax_fytd", "2026-08-01")] == 2.6452
    assert out[("cga_income_tax_fytd", "2026-08-01")] == 4.9545
    assert out[("cga_direct_tax_fytd", "2026-08-01")] == 7.5997
    assert out[("cga_gross_tax_fytd", "2026-03-01")] == 40.2435    # previous year, March (Prov.)
    assert ("cga_gross_tax_fytd", "2026-09-01") not in out


def test_heading_variants():
    assert prefix_of("CORPORATION TAX") == prefix_of("CORPORATE TAX") == "cga_corporate_tax"
    assert prefix_of("INCOME TAX") == prefix_of("TAXES ON INCOME OTHER THAN CORPORATE TAX ") == "cga_income_tax"
    assert prefix_of("GOODS AND SERVICE TAX COMPENSATION CESS") is None
