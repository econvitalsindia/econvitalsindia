"""Daily closes from Yahoo Finance (via the yfinance library): Indian indices and commodities.

Licence: show-only. Exchange index data and futures prices are shown with attribution,
never offered for download (AGENTS.md hard rule 6). Yahoo closes for the Nifty 50 and
Sensex were checked equal to the closes RBI republishes (27 Oct 2026), so this source
and pipelines/sources/rbi/home_rates.py can both write those series.

Backfills BACKFILL of history when a series is short, otherwise fetches RECENT.
Today's bar is used only when it is final: Indian indices after 16:00 IST; never for
commodity futures, which trade almost round the clock (yesterday's settle is used).
"""
from __future__ import annotations

import hashlib
import json
import warnings
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.store import load_series

TICKERS = {
    "^NSEI": ("nifty50_close", "index"), "^BSESN": ("sensex_close", "index"),
    "^INDIAVIX": ("indiavix_close", "index"),
    "BZ=F": ("brent_usd", "commodity"), "GC=F": ("gold_usd_oz", "commodity"),
}
BACKFILL, RECENT, MIN_HISTORY = "10y", "1mo", 100
IST = ZoneInfo("Asia/Kolkata")


class YahooMarkets(Source):
    name = "yahoo_markets"
    series_ids = tuple(sid for sid, _ in TICKERS.values())

    def fetch(self) -> list[Raw]:
        import yfinance as yf  # imported lazily: heavy, and only this source needs it

        raws = []
        for ticker, (sid, _) in TICKERS.items():
            period = BACKFILL if len(load_series(sid)) < MIN_HISTORY else RECENT
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                hist = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=False)
            if hist.empty:
                raise RuntimeError(f"Yahoo returned no data for {ticker}")
            rows = [[i.strftime("%Y-%m-%d"), float(c)] for i, c in hist["Close"].dropna().items()]
            body = json.dumps({"ticker": ticker, "period": period, "rows": rows}).encode()
            raws.append(Raw(content=body, url=f"yfinance:{ticker}?period={period}",
                            fetched_at=datetime.now(timezone.utc),
                            sha256=hashlib.sha256(body).hexdigest(), suffix=".json"))
        return raws

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        now_ist = raws[0].fetched_at.astimezone(IST) if raws else datetime.now(IST)
        today = now_ist.date().isoformat()
        out = []
        for raw in raws:
            body = json.loads(raw.content)
            sid, kind = TICKERS[body["ticker"]]
            final_today = kind == "index" and now_ist.hour >= 16
            out += [{"series_id": sid, "period": d, "value": round(v, 2), "note": "Yahoo Finance close"}
                    for d, v in body["rows"] if d < today or (d == today and final_today)]
        return pd.DataFrame(out)


SOURCE = YahooMarkets()
