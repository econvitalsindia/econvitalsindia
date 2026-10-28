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

    def dump(self) -> str:
        return json.dumps(self.receipts, indent=1, ensure_ascii=False)
