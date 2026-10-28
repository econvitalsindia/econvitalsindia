"""SIAM monthly press releases: three wording variants."""
from pipelines.sources.siam.sales import is_sales_release, parse_release, text_of
from tests.conftest import FIXTURES


def rows(release_id: int) -> dict:
    text = text_of((FIXTURES / "siam" / f"release_{release_id}.html").read_bytes())
    assert is_sales_release(text)
    return {(r["series_id"], r["period"]): r["value"] for r in parse_release(text)}


def test_april_2021_singular_was_and_pv_dropped():
    got = rows(482)        # "Three-wheeler sales was 13,728 units in April 2021"
    assert got == {("auto_3w_sales", "2021-04-01"): 13728.0, ("auto_2w_sales", "2021-04-01"): 995097.0}


def test_may_2026_stray_word():
    got = rows(609)        # "Two-wheeler sales were units 19,02,209 units in May 2026"
    assert got[("auto_2w_sales", "2026-05-01")] == 1902209.0
    assert got[("auto_pv_sales", "2026-05-01")] == 438854.0


def test_quarter_end_skips_quarter_totals():
    got = rows(622)        # also has "... units in July-September 2026"
    assert got == {("auto_pv_sales", "2026-09-01"): 454574.0, ("auto_3w_sales", "2026-09-01"): 98162.0,
                   ("auto_2w_sales", "2026-09-01"): 2463103.0}
