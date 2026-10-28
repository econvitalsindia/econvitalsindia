"""Daily snapshot of the rates panel on the RBI home page (https://www.rbi.org.in/).

The page shows the current policy corridor, reserve ratios, FBIL reference
exchange rates (as at 1 pm today), and "Market Trends": benchmark G-sec yields,
T-bill cut-offs and the Sensex and Nifty 50 closes (each "as on" a stated date).
It has no history, so each run upserts one observation per series. History builds
up from daily runs; older history comes from other sources (e.g. FBIL, DBIE).

Period conventions:
- policy rates and ratios: the IST date the page was read (the rate in force that day);
- exchange rates: the date in "(As at 1.00pm of <date>)";
- G-sec yields, Sensex, Nifty: the date in the "# as on" / "* as on" footnote;
- T-bills: the cut-off at the last auction, recorded against the read date.
"""
from __future__ import annotations

import html
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://www.rbi.org.in/"
NUM = r"([0-9][0-9,]*\.?[0-9]*)"


def page_text(content: bytes) -> str:
    """Collapse the HTML into ' | '-separated text cells."""
    t = content.decode("utf-8", errors="ignore")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " | ", t))
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"(\|\s*)+", "| ", t)


def _date(s: str) -> str:
    return datetime.strptime(s.strip(), "%B %d, %Y").date().isoformat()


def _value(text: str, label: str) -> float:
    m = re.search(re.escape(label) + r"\s*\|\s*:\s*" + NUM, text)
    if not m:
        raise ValueError(f"label not found on RBI home page: {label!r}")
    return float(m.group(1).replace(",", ""))


def ten_year_benchmark(text: str, year: int) -> tuple[str, float]:
    """The listed G-sec whose maturity year is closest to `year` + 10."""
    secs = re.findall(r"(\d+\.\d+% GS (\d{4}))\s*\|\s*:\s*" + NUM + "%", text)
    if not secs:
        raise ValueError("no G-sec yields found on RBI home page")
    name, _, value = min(secs, key=lambda s: abs(int(s[1]) - (year + 10)))
    return name, float(value)


class RbiHomeRates(Source):
    name = "rbi_home_rates"
    series_ids = ("repo_rate", "sdf_rate", "msf_rate", "crr", "slr", "usdinr_ref",
                  "gsec_10y_yield", "tbill_91d", "sensex_close", "nifty50_close")

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL, suffix=".html")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        text = page_text(raws[0].content)
        read_date = raws[0].fetched_at.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat()

        fx = re.search(r"As at 1\.00\s*pm of ([A-Za-z]+ \d{1,2}, \d{4})", text)
        markets = re.search(r"Government Securities Market.*?# \| as on \| ([A-Za-z]+ \d{1,2}, \d{4})", text)
        equities = re.search(r"Capital Market.*?\* \| as on \| ([A-Za-z]+ \d{1,2}, \d{4})", text)
        if not (fx and markets and equities):
            raise ValueError("date footnotes not found on RBI home page (layout changed?)")
        fx_date, mkt_date, eq_date = (_date(m.group(1)) for m in (fx, markets, equities))
        bench_name, bench_yield = ten_year_benchmark(text, int(mkt_date[:4]))

        rows = [
            ("repo_rate", read_date, _value(text, "Policy Repo Rate"), ""),
            ("sdf_rate", read_date, _value(text, "Standing Deposit Facility Rate"), ""),
            ("msf_rate", read_date, _value(text, "Marginal Standing Facility Rate"), ""),
            ("crr", read_date, _value(text, "CRR"), ""),
            ("slr", read_date, _value(text, "SLR"), ""),
            ("usdinr_ref", fx_date, _value(text, "INR / 1 USD"), "FBIL reference rate via RBI"),
            ("gsec_10y_yield", mkt_date, bench_yield, f"benchmark {bench_name}"),
            ("tbill_91d", read_date, _value(text, "91 day T-bills"), "cut-off at the last auction"),
            ("sensex_close", eq_date, _value(text, "S&P BSE Sensex"), ""),
            ("nifty50_close", eq_date, _value(text, "Nifty 50"), ""),
        ]
        return pd.DataFrame(rows, columns=["series_id", "period", "value", "note"])


SOURCE = RbiHomeRates()
