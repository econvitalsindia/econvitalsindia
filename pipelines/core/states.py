"""Canonical state / UT names (registry/states.yaml). Publishers spell them differently."""
from __future__ import annotations

import re
from functools import lru_cache

import yaml

from pipelines.core.store import ROOT


def _key(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower().replace("&", "and"))


@lru_cache(maxsize=1)
def _lookup() -> tuple[dict[str, str], set[str]]:
    reg = yaml.safe_load((ROOT / "registry" / "states.yaml").read_text())
    table = {}
    for canonical, aliases in reg["states"].items():
        for n in [canonical, *aliases]:
            table[_key(n)] = canonical
    return table, {_key(a) for a in reg["aggregates"]}


def canonical(name: str) -> str | None:
    """Canonical state name; None for all-India aggregates; ValueError if unknown."""
    table, aggregates = _lookup()
    k = _key(name)
    if k in aggregates:
        return None
    if k not in table:
        raise ValueError(f"unknown state name {name!r}: add it to registry/states.yaml")
    return table[k]
