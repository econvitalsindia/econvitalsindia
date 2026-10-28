"""Turn registry + data/ into the JSON the Astro site reads (site/src/data/generated/).

    python -m pipelines.build.site_data

Everything numeric on the site comes from here (AGENTS.md hard rule 2). Pages
never compute values themselves; they read these files. Files are only ever
overwritten, never deleted (project rule); the site reads series listed in
catalogue.json, so a leftover file for a removed series is simply ignored.
"""
from __future__ import annotations

import json
import sys
from datetime import date

import pandas as pd
import yaml

from pipelines.build import calendar
from pipelines.core import registry, store

OUT = store.ROOT / "site" / "src" / "data" / "generated"
PUBLIC = store.ROOT / "site" / "public" / "data"
PAGES = store.ROOT / "registry" / "pages"


def load(series_id: str) -> pd.DataFrame:
    """Stored series with period as Timestamp, sorted."""
    df = store.load_series(series_id)
    df["period"] = pd.to_datetime(df["period"])
    df["value"] = df["value"].astype(float)
    return df.sort_values("period").reset_index(drop=True)


def transform(df: pd.DataFrame, how: str) -> pd.DataFrame:
    """Apply a transform from 02-conventions.md. Changes match calendar periods, not row offsets."""
    s = df.set_index("period")["value"]
    if how == "level":
        out = s
    elif how in ("yoy", "mom"):
        offset = pd.DateOffset(years=1) if how == "yoy" else pd.DateOffset(months=1)
        prior = s.reindex(s.index - offset)
        out = pd.Series((s.values / prior.values - 1) * 100, index=s.index).dropna()
    elif how == "diff":
        out = s.diff().dropna() * 100  # percentage points -> basis points
    elif how in ("7dma", "7dma_yoy"):
        # 7-day calendar-window average (needs at least 5 observations in the window).
        ma = s.rolling("7D", min_periods=5).mean().dropna()
        if how == "7dma":
            out = ma
        else:
            prior = ma.reindex(ma.index - pd.DateOffset(years=1))
            out = pd.Series((ma.values / prior.values - 1) * 100, index=ma.index).dropna()
    else:
        raise ValueError(f"transform {how!r} not implemented in site build")
    return out.rename("value").reset_index()


def value_on_or_before(df: pd.DataFrame, when: pd.Timestamp, max_gap_days: int) -> float | None:
    """Last value on or before `when`, if it is no more than max_gap_days older than `when`.

    The gap limit stops a "1-day change" being computed against a week-old value
    when the series has holes (e.g. FBIL's delayed public feed).
    """
    prior = df[(df["period"] <= when) & (df["period"] >= when - pd.Timedelta(days=max_gap_days))]
    return None if prior.empty else float(prior["value"].iloc[-1])


# Largest gap (days) between a reference date and the observation used for it, by
# frequency: (1-day, 1-week, year-start). None = change not shown for that frequency.
GAP_LIMITS = {"D": (4, 3, 7), "W": (None, 9, 21), "F": (None, None, 30)}
STEP_GAP = 60  # step series (policy rates) hold their value until changed


def changes(df: pd.DataFrame, unit: str, freq: str, step: bool) -> dict | None:
    """1-day, 1-week and calendar-YTD changes (bp for rates, % otherwise).

    Step series (registry `step: true`, e.g. the repo rate) carry their last value
    forward, so any observation within STEP_GAP days is a valid reference.
    """
    limits = (STEP_GAP,) * 3 if step else GAP_LIMITS.get(freq)
    if limits is None:
        return None
    last_p, last_v = df["period"].iloc[-1], float(df["value"].iloc[-1])
    targets = (last_p - pd.Timedelta(days=1), last_p - pd.Timedelta(days=7),
               pd.Timestamp(year=last_p.year - 1, month=12, day=31))
    out = {}
    for key, target, gap in zip(("d1", "w1", "ytd"), targets, limits):
        ref = None if gap is None else value_on_or_before(df, target, max_gap_days=gap)
        if ref is None:
            out[key] = None
        elif unit == "percent":
            out[key] = round((last_v - ref) * 100, 1)       # basis points
        else:
            out[key] = round((last_v / ref - 1) * 100, 2)   # percent change
    out["kind"] = "bp" if unit == "percent" else "pct"
    return out


def series_payload(series_id: str, spec: dict, df: pd.DataFrame) -> dict:
    transforms = {t: [[p.strftime("%Y-%m-%d"), round(v, 4)]
                      for p, v in transform(df, t).itertuples(index=False)]
                  for t in spec["transforms"] if t != "level"}
    return {
        "id": series_id,
        "title": spec["title"],
        "short_title": spec["short_title"],
        "area": spec["area"],
        "unit": spec["unit"],
        "frequency": spec["frequency"],
        "base_year": spec.get("base_year"),
        "source": spec["source"],
        "licence": spec["licence"],
        "downloadable": spec["downloadable"],
        "notes": spec.get("notes", ""),
        "original": bool(spec.get("original")),
        "data": [[p.strftime("%Y-%m-%d"), v, n] for p, v, n in
                 zip(df["period"], df["value"], df["note"].fillna(""))],
        "transforms": transforms,
        "changes": changes(df, spec["unit"], spec["frequency"], bool(spec.get("step"))),
    }


def tile(spec: dict, payload: dict) -> dict:
    """One home-page tile: latest value of the requested transform plus its period."""
    how = spec.get("transform", "level")
    points = payload["data"] if how == "level" else payload["transforms"][how]
    period, value = points[-1][0], points[-1][1]
    # Same period a year earlier, matched on the date (not on row position).
    lag = {"M": pd.DateOffset(years=1), "Q": pd.DateOffset(years=1)}.get(payload["frequency"])
    year_ago = None
    if lag is not None:
        target = (pd.Timestamp(period) - lag).strftime("%Y-%m-%d")
        year_ago = next((v for p, v, *_ in points if p == target), None)
    return {**spec, "period": period, "value": value, "year_ago": year_ago,
            "unit": "percent" if how in ("yoy", "mom") else payload["unit"],
            "frequency": payload["frequency"], "changes": payload["changes"],
            "title": spec.get("label") or payload["short_title"],
            "note": payload["data"][-1][2] if how == "level" else ""}


def cpi_contributions() -> list[dict]:
    """Percentage-point contributions of food, fuel and core to headline CPI inflation.

    contribution_k(t) = w_k * (I_k(t) - I_k(t-12)) / I_general(t-12), which sums to the
    headline y/y rate because CPI 2024 is a fixed-weight index. Weights:
    registry/weights/cpi2024_core.yaml.
    """
    w = yaml.safe_load((store.ROOT / "registry" / "weights" / "cpi2024_core.yaml").read_text())
    parts = {"Food and beverages": ("cpi_food_bev_index", w["food_and_beverages"]),
             "Fuel": ("cpi_fuel_index", w["electricity_gas_fuels"] + w["vehicle_fuels"]),
             "Core": ("cpi_core_index", w["core"])}
    general = load("cpi_headline_index").set_index("period")["value"]
    rows = []
    for label, (sid, weight) in parts.items():
        s = load(sid).set_index("period")["value"]
        prior = s.reindex(s.index - pd.DateOffset(years=1)).values
        base = general.reindex(s.index - pd.DateOffset(years=1)).values
        contrib = pd.Series(weight * (s.values - prior) / base, index=s.index).dropna()
        rows += [{"period": p.strftime("%Y-%m-%d"), "component": label, "pp": round(v, 3)}
                 for p, v in contrib.items()]
    return rows


def question_metric(spec: dict, payload: dict) -> dict:
    """One number on a home-page question card: latest, year-ago or 4-period average."""
    how = spec.get("transform", "level")
    points = payload["data"] if how == "level" else payload["transforms"][how]
    period, value = points[-1][0], points[-1][1]
    if spec["stat"] == "year_ago":
        target = (pd.Timestamp(period) - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
        period, value = target, next((v for p, v, *_ in points if p == target), None)
    elif spec["stat"] == "avg4":
        last4 = points[-4:]
        period, value = f"{last4[0][0]}/{last4[-1][0]}", round(sum(p[1] for p in last4) / len(last4), 2)
    return {**spec, "period": period, "value": value, "frequency": payload["frequency"]}


def write_json(path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def main() -> int:
    specs = registry.all_series()
    payloads = {}
    for sid, spec in specs.items():
        df = load(sid)
        if df.empty:
            continue
        payloads[sid] = series_payload(sid, spec, df)
        write_json(OUT / "series" / f"{sid}.json", payloads[sid])

    pages = {f.stem: yaml.safe_load(f.read_text()) for f in sorted(PAGES.glob("*.yaml"))}
    tiles = [tile(t, payloads[t["series"]]) for t in pages.get("home", {}).get("tiles", [])
             if t["series"] in payloads]
    questions = [{**q, "metrics": [question_metric(m, payloads[m["series"]]) for m in q["metrics"]
                                   if m["series"] in payloads]}
                 for q in pages.get("home", {}).get("questions", [])]
    write_json(OUT / "home.json", {"tiles": tiles, "questions": questions})
    write_json(OUT / "cpi_contributions.json", cpi_contributions())

    catalogue = [{"id": sid, "title": spec["title"], "short_title": spec["short_title"],
                  "area": spec["area"], "agency": spec["source"]["agency"],
                  "source_url": spec["source"].get("url", ""), "frequency": spec["frequency"],
                  "unit": spec["unit"], "base_year": spec.get("base_year"),
                  "licence": spec["licence"], "downloadable": spec["downloadable"],
                  "fetch": spec["fetch"], "notes": spec.get("notes", ""),
                  "first_period": payloads[sid]["data"][0][0] if sid in payloads else None,
                  "last_period": payloads[sid]["data"][-1][0] if sid in payloads else None,
                  "observations": len(payloads[sid]["data"]) if sid in payloads else 0}
                 for sid, spec in specs.items()]
    write_json(OUT / "catalogue.json", catalogue)

    # Release calendar, with each release's latest published value attached.
    today = date.today().isoformat()
    cal = calendar.load(set(specs))
    for r in cal:
        r["status"] = "released" if r["date"] <= today else "upcoming"
        sid = r["series"][0] if r["series"] else None
        if sid in payloads:
            pts = payloads[sid]["data"] if r["show"] == "level" else payloads[sid]["transforms"][r["show"]]
            unit = "percent" if r["show"] in ("yoy", "mom") else payloads[sid]["unit"]
            r["latest"] = {"series": sid, "period": pts[-1][0], "value": pts[-1][1], "unit": unit,
                           "frequency": payloads[sid]["frequency"], "title": payloads[sid]["short_title"],
                           "show": r["show"]}
    write_json(OUT / "calendar.json", cal)
    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    (PUBLIC.parent / "calendar.ics").write_text(calendar.ics(cal, registry.site_config()["site"]["name"]))

    as_of = max((p["data"][-1][0] for p in payloads.values()), default=None)
    write_json(OUT / "site.json", {"built_on": date.today().isoformat(), "as_of": as_of,
                                   "status": store.load_status()})

    # Downloadable CSVs (licence permitting) are copied into the site's public folder.
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for sid, spec in specs.items():
        if spec["downloadable"] and sid in payloads:
            (PUBLIC / f"{sid}.csv").write_bytes((store.SERIES / f"{sid}.csv").read_bytes())
    leaked = [f.name for f in PUBLIC.glob("*.csv")
              if f.stem not in specs or not specs[f.stem]["downloadable"]]
    if leaked:
        print(f"ERROR: public CSVs for non-downloadable or unregistered series: {leaked}. "
              f"A maintainer must remove them from site/public/data/.")
        return 1

    print(f"built {len(payloads)} series, {len(tiles)} tiles -> {OUT.relative_to(store.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
