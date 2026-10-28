"""RBI Weekly Statistical Supplement (WSS): FX reserves, bank business, ratios and rates.

Archive pages list every week's table as XLSX:
  https://www.rbi.org.in/Scripts/WSSViewDetail.aspx?TYPE=Section&PARAM1=<n>
  n=2 Foreign Exchange Reserves (weekly, "As on <Friday>")
  n=3 Scheduled Commercial Banks - Business in India (fortnightly "Outstanding as on <date>")
  n=4 Ratios and Rates (six "week ended" columns, the first a year earlier)
Files are printed tables, so rows are found by their label and dates by their header.
The first run backfills BACKFILL_WEEKS files per section; later runs take RECENT_WEEKS.
Overlapping weeks are harmless: publishing upserts by period.
"""
from __future__ import annotations

import io
import re
from datetime import date, datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw, get
from pipelines.core.store import load_series

ARCHIVE = "https://www.rbi.org.in/Scripts/WSSViewDetail.aspx?TYPE=Section&PARAM1={n}"
BACKFILL_WEEKS, RECENT_WEEKS = 60, 6
SECTION = {2: "fx", 3: "banks", 4: "rates"}

FX_ROWS = {"Total Reserves": "fx_reserves_total", "Foreign Currency Assets": "fx_reserves_fca",
           "Gold": "fx_reserves_gold"}
BANK_LEVELS = {"2.1 Aggregate Deposits": "scb_deposits", "7 Bank Credit": "scb_credit",
               "7a.2 Non-food credit": "scb_nonfood_credit"}
BANK_GROWTH = {"2.1a Growth": "scb_deposits_growth", "7.1a Growth": "scb_credit_growth"}
RATE_ROWS = {
    "Cash Reserve Ratio": "crr", "Statutory Liquidity Ratio": "slr", "Policy Repo Rate": "repo_rate",
    "Standing Deposit Facility": "sdf_rate", "Marginal Standing Facility": "msf_rate",
    "Call Money Rate": "wacr", "91-Day Treasury Bill": "tbill_91d_weekly",
    "182-Day Treasury Bill": "tbill_182d_weekly", "364-Day Treasury Bill": "tbill_364d_weekly",
    "10-Year G-Sec Par Yield": "gsec_10y_par_fbil",
}
MONTH = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"


def parse_date(text: str, year: int | None = None) -> str | None:
    """'October 16, 2026' / 'Oct. 15, 2026' / ('Sep. 18', 2026) -> ISO date."""
    m = re.search(MONTH + r"\s*(\d{1,2})(?:,\s*(\d{4}))?", str(text))
    if not m:
        return None
    y = int(m.group(3)) if m.group(3) else year
    if y is None:
        return None
    return datetime.strptime(f"{m.group(1)} {m.group(2)} {y}", "%b %d %Y").date().isoformat()


def label(row) -> str:
    return " ".join(str(v) for v in row if isinstance(v, str)).strip()


def numbers(row) -> list[float]:
    out = []
    for v in row:
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            continue
    return [x for x in out if pd.notna(x)]


def parse_fx(df: pd.DataFrame) -> list[dict]:
    as_on = next(d for d in (parse_date(v) for v in df.values.ravel() if isinstance(v, str)
                             and "As on" in v) if d)
    usd_col = next(c for c in df.columns if (df[c].astype(str).str.strip() == "US$ Mn.").any())
    rows = []
    for _, r in df.iterrows():
        text = label(r)
        sid = next((s for k, s in FX_ROWS.items() if re.match(r"^1(\.\d)?\s+" + k, text)), None)
        if sid and pd.notna(r[usd_col]):
            rows.append({"series_id": sid, "period": as_on, "value": float(r[usd_col]) / 1000})
    return rows


def parse_banks(df: pd.DataFrame) -> list[dict]:
    as_on = next(d for d in (parse_date(v) for v in df.values.ravel() if isinstance(v, str)
                             and "as on" in v.lower()) if d)
    rows = []
    for _, r in df.iterrows():
        text, nums = label(r), numbers(r)
        for key, sid in BANK_LEVELS.items():
            if text.startswith(key) and nums:
                rows.append({"series_id": sid, "period": as_on, "value": nums[0] / 1e5})
        for key, sid in BANK_GROWTH.items():
            if text.startswith(key) and nums:
                # Last column is year-on-year growth for the current year, as published.
                rows.append({"series_id": sid, "period": as_on, "value": nums[-1]})
    return rows


def parse_rates(df: pd.DataFrame) -> list[dict]:
    header = df.index[df.apply(lambda r: label(r).startswith("Item/Week Ended"), axis=1)][0]
    years, dates = df.loc[header], df.loc[header + 1]
    col_date, year = {}, None
    for c in df.columns:
        if pd.notna(years[c]) and str(years[c]).strip().isdigit():
            year = int(str(years[c]).strip())
        d = parse_date(dates[c], year) if pd.notna(dates[c]) else None
        if d:
            col_date[c] = d
    rows = []
    for _, r in df.loc[header + 2:].iterrows():
        text = label(r)
        sid = next((s for k, s in RATE_ROWS.items() if text.startswith(k)), None)
        if not sid:
            continue
        for c, d in col_date.items():
            try:
                rows.append({"series_id": sid, "period": d, "value": float(r[c])})
            except (TypeError, ValueError):
                continue
    return rows


PARSERS = {2: parse_fx, 3: parse_banks, 4: parse_rates}
# Table titles printed in each file (the section is read from the file, not its name).
TITLES = {"Foreign Exchange Reserves": 2, "Scheduled Commercial Banks - Business in India": 3,
          "Ratios and Rates": 4}


def section_of(df: pd.DataFrame) -> int:
    text = " ".join(str(v) for v in df.head(4).values.ravel() if isinstance(v, str))
    for title, n in TITLES.items():
        if title in text:
            return n
    raise ValueError(f"unrecognised WSS table: {text[:80]!r}")
# Series per section: if any has little history yet, that section backfills.
MIN_HISTORY = 20
SECTION_SERIES = {2: list(FX_ROWS.values()),
                  3: [*BANK_LEVELS.values(), *BANK_GROWTH.values()],
                  4: list(dict.fromkeys(RATE_ROWS.values()))}


class RbiWSS(Source):
    name = "rbi_wss"
    series_ids = (*FX_ROWS.values(), *BANK_LEVELS.values(), *BANK_GROWTH.values(),
                  *dict.fromkeys(RATE_ROWS.values()))

    def fetch(self) -> list[Raw]:
        raws = []
        for n in SECTION:
            page = get(ARCHIVE.format(n=n)).text
            links = list(dict.fromkeys(re.findall(
                r'https://rbidocs\.rbi\.org\.in/rdocs/Wss/DOCs/\d+T_[0-9A-F]+\.XLSX', page)))
            if not links:
                raise RuntimeError(f"no WSS XLSX links on section {n} archive page")
            short = any(len(load_series(s)) < MIN_HISTORY for s in SECTION_SERIES[n])
            take = BACKFILL_WEEKS if short else RECENT_WEEKS
            for url in links[:take]:
                raws.append(fetch_raw(url, suffix=".xlsx"))
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows = []
        for raw in raws:
            df = pd.read_excel(io.BytesIO(raw.content), header=None).dropna(how="all").dropna(axis=1, how="all")
            df = df.reset_index(drop=True)
            df.columns = range(df.shape[1])
            rows += PARSERS[section_of(df)](df)
        out = pd.DataFrame(rows)
        # Several files cover the same week (the rates table repeats recent weeks), and RBI
        # revises earlier prints. Raws arrive newest publication first, so keep the first
        # value seen for each week: the latest published one.
        conflicts = out.groupby(["series_id", "period"])["value"].nunique()
        conflicts = conflicts[conflicts > 1]
        if len(conflicts):
            print(f"  WSS: {len(conflicts)} week(s) revised between prints; keeping the latest print: "
                  f"{[f'{s} {p}' for s, p in conflicts.index[:5]]}")
        out = out.drop_duplicates(subset=["series_id", "period"], keep="first")
        out["note"] = "RBI WSS"
        return out[out["period"] <= date.today().isoformat()]


SOURCE = RbiWSS()
