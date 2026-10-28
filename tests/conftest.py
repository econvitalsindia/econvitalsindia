"""Shared test helpers."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pipelines.core import Raw

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def raw_from():
    """Build a Raw from a fixture file, as if fetched at `when` (UTC)."""
    def make(rel: str, when: datetime = datetime(2026, 10, 28, 10, 0, tzinfo=timezone.utc)) -> Raw:
        content = (FIXTURES / rel).read_bytes()
        return Raw(content=content, url=f"fixture://{rel}", fetched_at=when,
                   sha256=hashlib.sha256(content).hexdigest(), suffix=Path(rel).suffix)
    return make
