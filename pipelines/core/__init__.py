"""Shared pipeline code. Every data source subclasses `Source`.

Contract (docs/guidebook/01-architecture.md):
    fetch()    -> Raw (bytes + receipt). Saved to data/raw/, never committed.
    parse()    -> tidy DataFrame with columns: series_id, period, value, vintage.
    validate() -> list of problems; non-empty means nothing is published.
    publish()  -> writes data/series/<id>.csv, data/meta/<id>.json, updates data/status.json.

A failure at any step leaves existing data untouched and marks the series stale.
Implemented in Phase 1.
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
    suffix: str  # file extension, e.g. ".xlsx"


class Source(ABC):
    """One publisher dataset; may produce several series ids."""

    series_ids: tuple[str, ...] = ()

    @abstractmethod
    def fetch(self) -> Raw:
        """Download the latest release."""

    @abstractmethod
    def parse(self, raw: Raw) -> pd.DataFrame:
        """Return tidy rows: series_id, period (ISO period start), value, vintage."""
