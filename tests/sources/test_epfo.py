"""EPFO net payroll, pinned to the report of September 2025 (the last one posted)."""
import io

import pdfplumber

from pipelines.sources.epfo.payroll import parse_report, report_date


def test_monthly_rows_only(raw_from):
    raw = raw_from("epfo/September-2025.pdf")
    rows = parse_report(pdfplumber.open(io.BytesIO(raw.content)).pages[0].extract_text())
    got = {r["period"]: r["value"] for r in rows}
    assert got == {"2025-04-01": 14.3164, "2025-05-01": 14.6247,     # lakh; financial-year rows skipped
                   "2025-06-01": 19.0453, "2025-07-01": 21.0436}


def test_report_date_from_url():
    assert report_date("https://x/uploads/2025/10/September-2025.pdf") == "2025-09-01"
    assert report_date("https://x/uploads/2025/10/May-2021-1.pdf") == "2021-05-01"
