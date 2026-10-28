"""Read the series registry (registry/series/*.yaml)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SERIES_DIR = ROOT / "registry" / "series"


@lru_cache(maxsize=1)
def all_series() -> dict[str, dict]:
    """Every series yaml keyed by id (templates starting with '_' excluded)."""
    out = {}
    for f in sorted(SERIES_DIR.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        spec = yaml.safe_load(f.read_text())
        out[spec["id"]] = spec
    return out


def series(series_id: str) -> dict:
    """One series' registry entry; KeyError if it is not registered."""
    return all_series()[series_id]


def site_config() -> dict:
    """site.config.yaml as a dict."""
    return yaml.safe_load((ROOT / "site.config.yaml").read_text())
