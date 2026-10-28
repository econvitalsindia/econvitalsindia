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


def changes(df: pd.DataFrame, unit: str) -> dict:
    """1-day, 1-week and calendar-YTD changes for daily series (bp for rates, % otherwise)."""
    last_p, last_v = df["period"].iloc[-1], float(df["value"].iloc[-1])
    refs = {
        "d1": value_on_or_before(df, last_p - pd.Timedelta(days=1), max_gap_days=4),
        "w1": value_on_or_before(df, last_p - pd.Timedelta(days=7), max_gap_days=3),
        "ytd": value_on_or_before(df, pd.Timestamp(year=last_p.year - 1, month=12, day=31),
                                  max_gap_days=7),
    }
    out = {}
    for k, ref in refs.items():
        if ref is None:
            out[k] = None
        elif unit == "percent":
            out[k] = round((last_v - ref) * 100, 1)       # basis points
        else:
            out[k] = round((last_v / ref - 1) * 100, 2)   # percent change
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
        "data": [[p.strftime("%Y-%m-%d"), v, n] for p, v, n in
                 zip(df["period"], df["value"], df["note"].fillna(""))],
        "transforms": transforms,
        "changes": changes(df, spec["unit"]) if spec["frequency"] == "D" else None,
    }


def tile(spec: dict, payload: dict) -> dict:
    """One home-page tile: latest value of the requested transform plus its period."""
    how = spec.get("transform", "level")
    points = payload["data"] if how == "level" else payload["transforms"][how]
    period, value = points[-1][0], points[-1][1]
    year_ago = None
    if payload["frequency"] == "M" and len(points) > 12:
        year_ago = points[-13][1]
    return {**spec, "period": period, "value": value, "year_ago": year_ago,
            "unit": "percent" if how in ("yoy", "mom") else payload["unit"],
            "frequency": payload["frequency"], "changes": payload["changes"],
            "title": spec.get("label") or payload["short_title"],
            "note": payload["data"][-1][2] if how == "level" else ""}


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
    write_json(OUT / "home.json", {"tiles": tiles})

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
