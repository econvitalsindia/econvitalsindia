"""State government finances, from RBI's Handbook of Statistics on Indian States.

The Handbook page (AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+States)
lists each table as "Table N: <title>" with an XLSX link whose name changes every edition,
so tables are found by number. Tables used:
  21  Gross State Domestic Product (Current Prices), Rs lakh, base 2011-12
  164 State-wise Gross Fiscal Deficit, Rs crore   (minus = surplus)
  165 State-wise Revenue Deficit, Rs crore        (minus = surplus)
  170 State-wise Interest Payments, Rs crore
  176 Composition of Outstanding Liabilities, one pair of sheets per end-March; the
      "(Concld.)" sheet has the "Outstanding Liabilities" total, Rs crore.
Year columns read "2022-23 (A)", "2023-24 (RE)", "2024-25 (BE)": the stage goes in the
note. Each table is split across sheets ("T_164(i)", "T_164(ii)"); all are read.

Panels (entity = state; period = 1 April of the financial year; Rs lakh crore):
state_gsdp_current, state_gfd, state_revenue_deficit, state_interest, state_liabilities
(end-March of the year, so end-March 2025 -> 2024-04-01). "All States and UTs" is dropped
(registry/states.yaml aggregates) after checking that the states add up to it: a year
whose rows don't (e.g. end-March 2015 in Table 176, where a missing "Telangana" label shifts
every value below it by one row) is dropped with a message rather than repaired.
"""
from __future__ import annotations

import html
import io
import re

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.states import canonical

PAGE = "https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+States"
TABLES = {21: ("state_gsdp_current", 1e7), 164: ("state_gfd", 1e5), 165: ("state_revenue_deficit", 1e5),
          170: ("state_interest", 1e5), 176: ("state_liabilities", 1e5)}       # divisor to Rs lakh crore
FY = re.compile(r"(\d{4})-\d{2}\s*(?:\((A|RE|BE|AE|PE|QE)\))?")


def table_links(page: str) -> dict[int, str]:
    out = {}
    for title, url in re.findall(r"class='link2' href=PublicationsView\.aspx\?id=\d+>([^<]+)</a>.*?href='(https://rbidocs[^']+\.XLSX)'",
                                 page, re.S | re.I):
        m = re.match(r"\s*Table\s*(\d+)", html.unescape(title), re.I)
        if m and int(m.group(1)) in TABLES:
            out.setdefault(int(m.group(1)), url)
    return out


def state_of(label) -> str | None:
    text = re.sub(r"\s+", " ", str(label)).strip()
    if not text or text == "nan" or len(text) > 45:          # notes and sources run long
        return None
    try:
        return canonical(text)
    except ValueError:
        # Footnotes ("-: Not Available.", "Notes: ...") are skipped; anything that reads like
        # a place name must be in registry/states.yaml, so fail loudly.
        if re.fullmatch(r"[A-Za-z][A-Za-z &.'()-]*", text) and not re.match(r"(Notes?|Source|Sources)\b", text):
            raise
        return None


def is_total(label) -> bool:
    return re.sub(r"\s+", " ", str(label)).strip().lower().startswith("all states")


def adds_up(states: list[float], total: float | None) -> bool:
    """The publisher's own check: states add up to the "All States and UTs" row (1% slack
    for rounding). A column that fails has misaligned rows and is dropped."""
    return total is None or abs(sum(states) - total) <= max(0.01 * abs(total), 2)


def year_columns(df: pd.DataFrame) -> tuple[int, dict]:
    """(row after the header, {column: (period, stage)}) from the first rows with FY labels."""
    for i in range(min(10, len(df))):
        cols = {c: FY.fullmatch(str(v).strip()) for c, v in df.loc[i].items()}
        cols = {c: (f"{m.group(1)}-04-01", m.group(2) or "") for c, m in cols.items() if m}
        if len(cols) >= 3:
            return i + 1, cols
    raise ValueError("no financial-year header row")


def parse_years(book: pd.ExcelFile, sid: str, divisor: float) -> list[dict]:
    rows = []
    for sheet in book.sheet_names:
        df = pd.read_excel(book, sheet, header=None)
        start, cols = year_columns(df)
        label_col = 1 if df.shape[1] > 1 else 0
        for c, (period, stage) in cols.items():
            found, total = [], None
            for i in range(start, len(df)):
                v = pd.to_numeric(df.loc[i, c], errors="coerce")
                if is_total(df.iloc[i, label_col]):
                    total = None if pd.isna(v) else float(v)
                    continue
                st = state_of(df.iloc[i, label_col])
                if st and pd.notna(v):
                    found.append((st, float(v)))
            if not adds_up([v for _, v in found], total):
                print(f"  {sid} {period}: states add to {sum(v for _, v in found):.0f}, total row {total:.0f}; year dropped (rows misaligned in the source)")
                continue
            rows += [{"series_id": sid, "entity": st, "period": period, "value": round(v / divisor, 5),
                      "note": {"A": "Accounts", "RE": "Revised Estimates", "BE": "Budget Estimates"}.get(stage, stage)}
                     for st, v in found]
    return rows


def parse_liabilities(book: pd.ExcelFile, divisor: float) -> list[dict]:
    rows = []
    for sheet in book.sheet_names:
        df = pd.read_excel(book, sheet, header=None)
        title = " ".join(str(v) for v in df.head(4).values.ravel() if isinstance(v, str))
        year = re.search(r"OUTSTANDING LIABILITIES\s*-\s*(\d{4})", title)
        head = next((i for i in range(8) if df.loc[i].astype(str).str.contains("Outstanding Liabilities").any()), None)
        if not year or head is None:
            continue                                        # the first sheet of each pair has no total
        col = next(c for c in df.columns if "Outstanding Liabilities" in str(df.loc[head, c]))
        period = f"{int(year.group(1)) - 1}-04-01"          # end-March 2025 closes FY 2024-25
        found, total = [], None
        for i in range(head + 1, len(df)):
            v = pd.to_numeric(df.loc[i, col], errors="coerce")
            if is_total(df.iloc[i, 1]):
                total = None if pd.isna(v) else float(v)
                continue
            st = state_of(df.iloc[i, 1])
            if st and pd.notna(v):
                found.append((st, float(v)))
        if not adds_up([v for _, v in found], total):
            print(f"  state_liabilities end-March {year.group(1)}: states add to {sum(v for _, v in found):.0f}, "
                  f"total row {total:.0f}; year dropped (rows misaligned in the source)")
            continue
        rows += [{"series_id": "state_liabilities", "entity": st, "period": period, "value": round(v / divisor, 5),
                  "note": "end-March"} for st, v in found]
    return rows


class StateFinances(Source):
    name = "rbi_state_finances"
    panel = True
    series_ids = tuple(sid for sid, _ in TABLES.values())

    def fetch(self) -> list[Raw]:
        links = table_links(get(PAGE).text)
        missing = set(TABLES) - set(links)
        if missing:
            raise RuntimeError(f"Handbook tables not found on the page: {sorted(missing)}")
        return [fetch_raw(links[n], suffix=f".t{n}.xlsx") for n in sorted(links)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            n = int(re.search(r"/(\d+)T_", raw.url).group(1))
            sid, divisor = TABLES[n]
            book = pd.ExcelFile(io.BytesIO(raw.content))
            rows += parse_liabilities(book, divisor) if n == 176 else parse_years(book, sid, divisor)
        out = pd.DataFrame(rows)
        # A year printed on two sheets (or as A and RE) keeps the later sheet's value.
        return out.drop_duplicates(["series_id", "entity", "period"], keep="last")


SOURCE = StateFinances()
