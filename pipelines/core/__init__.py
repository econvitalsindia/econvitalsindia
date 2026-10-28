"""Shared pipeline code. Every data source subclasses `Source`.

Contract (docs/guidebook/01-architecture.md):
    fetch()    -> list[Raw]: downloaded files + receipts. Archived to data/raw/, never committed.
    parse()    -> tidy DataFrame with columns: series_id, period, value, [note].
    validate   -> done by pipelines.core.validate using each series' registry yaml.
    publish    -> done by pipelines.core.store: upserts into data/series/<id>.csv.

Publishing is an upsert: periods in the new data are added or revised, periods
not in the new data are kept. This lets snapshot sources (one value per day,
e.g. the RBI home page) build history, and full-history sources refresh it.
A failure at any step leaves existing data untouched and marks the series stale.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class Raw:
    """A downloaded file plus the receipt needed to trace every value back to it."""
    content: bytes
    url: str
    fetched_at: datetime
    sha256: str
    suffix: str  # file extension, e.g. ".json"


class Source(ABC):
    """One publisher dataset; may produce several series ids.

    Subclasses set `name` (unique, used on the command line) and `series_ids`
    (every id it can produce; each needs a registry/series yaml).
    """

    name: str = ""
    series_ids: tuple[str, ...] = ()
    # Derived sources compute from stored series instead of downloading; they run last.
    derived: bool = False
    # Panel sources return an extra "entity" column (e.g. state) and are stored in
    # data/panels/<id>.csv keyed on (entity, period).
    panel: bool = False

    @abstractmethod
    def fetch(self) -> list[Raw]:
        """Download everything parse() needs."""

    @abstractmethod
    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        """Return tidy rows: series_id, period (ISO date of period start), value, optional note."""
