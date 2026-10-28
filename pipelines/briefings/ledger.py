"""The number ledger: every number a briefing may print, with its source.

A briefing never types a number (docs/guidebook/07-editorial-policy.md). Templates use
tokens `{{<series_id>[:<transform>].<fact>}}`, e.g. `{{cpi_headline_inflation.latest}}` or
`{{cpi_core_index:yoy.latest}}`; the ledger resolves each token to formatted text and
records the series, period, value and source URL behind it.

Facts for each series view:
  latest, latest_period, prev, prev_period, year_ago, year_ago_period,
  change            latest - prev, in the unit's change wording (percentage points, %, ...)
  direction         "rose" / "fell" / "was unchanged" (latest vs prev)
  direction_noun    "an increase" / "a decrease" / "no change"
  change_yoy        latest - year_ago,   direction_yoy  (vs a year earlier)
  change_phrase     "up 0.71 percentage points" / "down ..." / "unchanged" (vs prev)
  change_phrase_yoy the same, vs a year earlier
  pct_phrase        "up 0.22%" / "down 1.10%" / "unchanged": % change vs prev (levels, not rates)
  bp_phrase         "up 25 basis points" / "unchanged": change vs prev, for per-cent series
  week_phrase       change over the 7 days to the latest observation (pct for levels, bp for
                    rates), only for daily/weekly series with an observation within 3 days of
                    a week earlier
Calendar facts (add_calendar): `{{calendar.today}}` (releases scheduled that day),
`{{calendar.next}}` (the next few) and `{{calendar.next_highlight}}` (next MPC decision etc.),
built from registry/calendar.
Constants (policy targets etc.) come from registry/briefings/constants.yaml as
`{{const.<name>}}`, each with its source.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import pandas as pd

from pipelines.build import site_data
from pipelines.core import registry

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
               "September", "October", "November", "December"]
MINUS = "−"


def fmt_period(iso: str, freq: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    if freq == "M":
        return f"{FULL_MONTHS[m - 1]} {y}"
    if freq == "Q":
        fy_end = y + 1 if m >= 4 else y
        return f"Q{((m - 4) % 12) // 3 + 1} FY{str(fy_end)[2:]}"
    if freq == "A":
        return f"{y}-{str(y + 1)[2:]}" if m in (4, 7) else str(y)
    return f"{d} {MONTHS[m - 1]} {y}"


def data_decimals(values) -> int:
    """Decimals the publisher uses (max over recent values, 0-2)."""
    def dec(x: float) -> int:
        s = f"{x:.6f}".rstrip("0").rstrip(".")
        return len(s.split(".")[1]) if "." in s else 0
    return min(2, max((dec(float(v)) for v in values), default=1))


def fmt_value(v: float, unit: str, decimals: int = 2) -> str:
    sign = MINUS if v < 0 else ""
    a = abs(v)
    if unit == "percent":
        return f"{sign}{a:.{decimals}f}%"
    if unit == "usd_bn":
        return f"{sign}${a:,.1f} billion"
    if unit == "inr_lakh_crore":
        return f"{sign}₹{a:,.2f} lakh crore"
    if unit == "index":
        return f"{sign}{a:,.2f}"
    return f"{sign}{a:,.2f}"


def fmt_change(d: float, unit: str, decimals: int = 2) -> str:
    a = abs(d)
    if unit == "percent":
        return f"{a:.{decimals}f} percentage points"
    if unit == "usd_bn":
        return f"${a:,.1f} billion"
    if unit == "inr_lakh_crore":
        return f"₹{a:,.2f} lakh crore"
    return f"{a:,.2f}"


def phrase(d: float, unit: str, decimals: int = 2) -> str:
    word, _ = direction(d)
    return "unchanged" if word == "was unchanged" else f"{'up' if d > 0 else 'down'} {fmt_change(d, unit, decimals)}"


def direction(d: float, tol: float = 1e-9) -> tuple[str, str]:
    if d > tol:
        return "rose", "an increase"
    if d < -tol:
        return "fell", "a decrease"
    return "was unchanged", "no change"


@dataclass
class Ledger:
    """Resolved facts keyed by token, plus provenance for each."""
    facts: dict[str, str] = field(default_factory=dict)
    receipts: dict[str, dict] = field(default_factory=dict)

    def add_view(self, series_id: str, how: str = "level") -> None:
        spec = registry.series(series_id)
        df = site_data.load(series_id)
        pts = site_data.transform(df, how) if how != "level" else df[["period", "value"]]
        pts = pts.dropna().sort_values("period").reset_index(drop=True)
        if pts.empty:
            return
        unit = "percent" if how in ("yoy", "mom", "7dma_yoy") else spec["unit"]
        raw_dec = data_decimals(df["value"].tail(12))
        # Published values keep the publisher's precision; growth computed from an index
        # keeps the index's precision (CPI: 2), otherwise one decimal.
        dec = (max(1, raw_dec) if how == "level"
               else (2 if spec["unit"] == "index" and raw_dec >= 2 else 1))
        key = series_id if how == "level" else f"{series_id}:{how}"
        last = pts.iloc[-1]
        prev = pts.iloc[-2] if len(pts) > 1 else None
        ya_target = last["period"] - pd.DateOffset(years=1)
        ya = pts[pts["period"] == ya_target]
        freq = spec["frequency"]
        put = {
            "latest": fmt_value(last["value"], unit, dec),
            "latest_period": fmt_period(last["period"].strftime("%Y-%m-%d"), freq),
        }
        if prev is not None:
            d = last["value"] - prev["value"]
            put.update(prev=fmt_value(prev["value"], unit, dec),
                       prev_period=fmt_period(prev["period"].strftime("%Y-%m-%d"), freq),
                       change=fmt_change(d, unit, dec))
            put["direction"], put["direction_noun"] = direction(d)
            put["change_phrase"] = phrase(d, unit, dec)
            if unit == "percent":
                bp = round(abs(d) * 100)
                put["bp_phrase"] = "unchanged" if bp == 0 else f"{'up' if d > 0 else 'down'} {bp} basis points"
            elif prev["value"]:
                pct = (last["value"] / prev["value"] - 1) * 100
                put["pct_phrase"] = ("unchanged" if round(pct, 2) == 0
                                     else f"{'up' if pct > 0 else 'down'} {abs(pct):.2f}%")
        if freq in ("D", "W"):
            target = last["period"] - pd.Timedelta(days=7)
            before = pts[(pts["period"] <= target) & (pts["period"] >= target - pd.Timedelta(days=3))]
            if len(before):
                ref = before["value"].iloc[-1]
                if unit == "percent":
                    bp = round((last["value"] - ref) * 100)
                    put["week_phrase"] = "unchanged" if bp == 0 else f"{'up' if bp > 0 else 'down'} {abs(bp)} basis points"
                elif ref:
                    pct = (last["value"] / ref - 1) * 100
                    put["week_phrase"] = ("unchanged" if round(pct, 2) == 0
                                          else f"{'up' if pct > 0 else 'down'} {abs(pct):.2f}%")
        if len(ya):
            d = last["value"] - ya["value"].iloc[0]
            put.update(year_ago=fmt_value(ya["value"].iloc[0], unit, dec),
                       year_ago_period=fmt_period(ya_target.strftime("%Y-%m-%d"), freq),
                       change_yoy=fmt_change(d, unit, dec))
            put["direction_yoy"], _ = direction(d)
            put["change_phrase_yoy"] = phrase(d, unit, dec)
        for fact, text in put.items():
            token = f"{key}.{fact}"
            self.facts[token] = text
            self.receipts[token] = {"series": series_id, "transform": how,
                                    "period": last["period"].strftime("%Y-%m-%d"),
                                    "source": spec["source"].get("url", ""), "text": text}

    def add_constants(self, path) -> None:
        import yaml
        for name, c in yaml.safe_load(path.read_text()).items():
            token = f"const.{name}"
            self.facts[token] = c["text"]
            self.receipts[token] = {"constant": name, "source": c["source"], "text": c["text"]}

    def add_calendar(self, on: str, upcoming: int = 4) -> None:
        """Releases scheduled on `on`, the next few after it, and the next highlighted
        event (e.g. an MPC decision), as text."""
        from pipelines.build import calendar as cal
        from pipelines.core.registry import all_series

        def item(r: dict) -> str:
            return f"{r['title']} ({r['period']})"

        def when(r: dict) -> str:
            return f"{item(r)} on {fmt_period(r['date'], 'D')}"

        rows = cal.load(set(all_series()))
        today = [r for r in rows if r["date"] == on]
        later = [r for r in rows if r["date"] > on]
        highlight = next((r for r in later if r["highlight"]), None)
        self.facts["calendar.today"] = "; ".join(item(r) for r in today) or "no scheduled releases"
        self.facts["calendar.next"] = "; ".join(when(r) for r in later[:upcoming]) or "none scheduled"
        start = (pd.Timestamp(on) - pd.Timedelta(days=6)).strftime("%Y-%m-%d")
        end = (pd.Timestamp(on) + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
        self.facts["calendar.past_week"] = ("; ".join(when(r) for r in rows if start <= r["date"] <= on)
                                            or "no scheduled releases")
        self.facts["calendar.next_week"] = ("; ".join(when(r) for r in rows if on < r["date"] <= end)
                                            or "no scheduled releases")
        self.facts["calendar.next_highlight"] = (f"{highlight['title']} on {fmt_period(highlight['date'], 'D')}"
                                                 if highlight else "not yet scheduled")
        for k in ("calendar.today", "calendar.next", "calendar.next_highlight",
                  "calendar.past_week", "calendar.next_week"):
            self.receipts[k] = {"source": "registry/calendar", "text": self.facts[k]}

    def dump(self) -> str:
        return json.dumps(self.receipts, indent=1, ensure_ascii=False)
