"""Yahoo source: only final daily bars are kept."""
import json
from datetime import datetime, timezone

from pipelines.core import Raw
from pipelines.sources.yahoo.markets import SOURCE


def raw(ticker, rows, fetched_utc):
    body = json.dumps({"ticker": ticker, "period": "1mo", "rows": rows}).encode()
    return Raw(body, f"yfinance:{ticker}", fetched_utc, "x", ".json")


def test_today_bar_rules():
    # 2026-10-28 11:00 UTC = 16:30 IST: Indian close is final; futures are still trading.
    t = datetime(2026, 10, 28, 11, 0, tzinfo=timezone.utc)
    rows = [["2026-10-27", 100.123], ["2026-10-28", 101.0]]
    df = SOURCE.parse([raw("^NSEI", rows, t), raw("BZ=F", rows, t)])
    assert set(df[df.series_id == "nifty50_close"].period) == {"2026-10-27", "2026-10-28"}
    assert set(df[df.series_id == "brent_usd"].period) == {"2026-10-27"}
    assert df[df.period == "2026-10-27"].value.iloc[0] == 100.12


def test_before_indian_close():
    t = datetime(2026, 10, 28, 6, 0, tzinfo=timezone.utc)  # 11:30 IST, market open
    df = SOURCE.parse([raw("^NSEI", [["2026-10-27", 1.0], ["2026-10-28", 2.0]], t)])
    assert list(df.period) == ["2026-10-27"]
