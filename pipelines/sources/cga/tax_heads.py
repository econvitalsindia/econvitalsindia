"""Union Government tax collections by head, monthly, Controller General of Accounts.

The monthly accounts link a "Monthly Trend" statement:
https://cga.nic.in/writereaddata/MonthAccount/<m><yyyy>/DTL3<fy>.HTM (some months .htm).
It has one table per tax head (gross tax revenue, corporate tax, taxes on income other than
corporate tax, STT, GST parts, customs, excise, ...), each with Monthly and Year-to-date
columns for the current and the previous financial year (₹ crore). The headings sit in the
text just before each table ("Monthly Trend Tax Revenue (Net) (CORPORATE TAX)").

Each year therefore appears twice: as the current year, then as the previous year in next
year's statements (where March is no longer provisional). Statements are read newest
first and the newest value wins. Stored as financial-year-to-date totals in ₹ lakh crore.

CBDT's own direct-tax releases on PIB stop after April 2024, so this is the direct-tax source.
"""
from __future__ import annotations

import io
import re
from html import unescape

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series
from pipelines.sources.cga.monthly_accounts import fy_code

URL = "https://cga.nic.in/writereaddata/MonthAccount/{m}{y}/DTL3{fy}.{ext}"
FIRST_FY = 2016                        # March 2017 statement: FY 2016-17 and 2015-16
# Heading start -> series prefix. Older statements say "CORPORATION TAX" and "INCOME TAX";
# newer ones "CORPORATE TAX" and "TAXES ON INCOME OTHER THAN CORPORATE TAX".
HEADS = [("GROSS TAX", "cga_gross_tax"), ("CORPORAT", "cga_corporate_tax"),
         ("TAXES ON INCOME", "cga_income_tax"), ("INCOME TAX", "cga_income_tax"),
         ("SECURITIES TRANSACTION", "cga_stt"), ("CUSTOMS", "cga_customs"),
         ("UNION EXCISE", "cga_excise")]
DERIVED = "cga_direct_tax"             # corporate + income tax (site calculation; excludes STT,
                                       # which has its own head only from FY 2023-24)
MONTHS = ["April", "May", "June", "July", "August", "September", "October", "November",
          "December", "January", "February", "March"]


def heads_of(html: str) -> list[str]:
    text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))
    return re.findall(r"Monthly Trend .{0,40}?\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*\*?\s*\(\s*refer", text)


def prefix_of(head: str) -> str | None:
    return next((p for k, p in HEADS if head.strip().upper().startswith(k)), None)


def parse_trend(html: str) -> tuple[tuple[int, int], dict[tuple[str, str], float]]:
    """(sort key, {(series_id, period): ₹ lakh crore}) from one statement."""
    heads = heads_of(html)
    tables = [t for t in pd.read_html(io.StringIO(html)) if t.shape[1] == 5]
    if not heads or len(heads) != len(tables):
        raise ValueError(f"{len(heads)} headings but {len(tables)} five-column tables")
    out, key = {}, None
    for head, t in zip(heads, tables):
        prefix = prefix_of(head)
        for col in (2, 4):                                   # Year-to-date columns
            start = int(str(t.iloc[0, col])[:4])
            for _, r in t.iloc[2:].iterrows():
                month = next((m for m in MONTHS if str(r[0]).strip().startswith(m)), None)
                if month is None or pd.isna(r[col]):
                    continue
                i = MONTHS.index(month)
                period = f"{start + (i >= 9)}-{(i + 3) % 12 + 1:02d}-01"
                if col == 2:
                    key = max(key or (0, 0), (start, i))
                if prefix:
                    out[(f"{prefix}_fytd", period)] = round(float(str(r[col]).replace(",", "")) / 1e5, 4)
    if key is None or not out:
        raise ValueError("no year-to-date values found")
    for (sid, period), v in list(out.items()):
        if sid == "cga_corporate_tax_fytd" and ("cga_income_tax_fytd", period) in out:
            out[(f"{DERIVED}_fytd", period)] = round(v + out[("cga_income_tax_fytd", period)], 4)
    return key, out


class CgaTaxHeads(Source):
    name = "cga_tax_heads"
    series_ids = (*dict.fromkeys(f"{p}_fytd" for _, p in HEADS), f"{DERIVED}_fytd")

    def get(self, p: pd.Period) -> Raw | None:
        for ext in ("HTM", "htm"):
            try:
                return fetch_raw(URL.format(m=p.month, y=p.year, fy=fy_code(p), ext=ext), suffix=".htm")
            except RuntimeError as e:
                if "404" not in str(e):
                    raise
        return None

    def fetch(self) -> list[Raw]:
        now = pd.Period.now(freq="M")
        latest = next((r for p in pd.period_range(now - 4, now, freq="M")[::-1] if (r := self.get(p))), None)
        if latest is None:
            raise RuntimeError("no CGA monthly-trend statement in the last five months")
        raws = [latest]
        # Backfill when any head with a long history is short (STT starts only in FY 2023-24).
        if min(len(load_series(s)) for s in self.series_ids if s != "cga_stt_fytd") < 36:
            last_march = now.year - 1 if now.month < 4 else now.year
            raws += [r for y in range(FIRST_FY + 1, last_march + 1)
                     if (r := self.get(pd.Period(f"{y}-03", freq="M")))]
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        parsed = sorted((parse_trend(r.content.decode("utf-8", "ignore")) for r in raws), reverse=True)
        values: dict[tuple[str, str], float] = {}
        for _, out in parsed:                                # newest statement first
            for k, v in out.items():
                values.setdefault(k, v)
        return pd.DataFrame([{"series_id": s, "period": p, "value": v} for (s, p), v in values.items()])


SOURCE = CgaTaxHeads()
