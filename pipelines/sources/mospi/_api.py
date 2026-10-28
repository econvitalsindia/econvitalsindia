"""Shared helpers for MoSPI's eSankhyiki REST API (https://api.mospi.gov.in/api/<product>/...).

No key is needed. Page size limits differ by dataset (100 is safe everywhere).
Specs: https://esankhyiki.mospi.gov.in/layout/swagger_user_<product>.yaml
Filter codes: MCP server https://mcp.mospi.gov.in/mcp, tool get_metadata.
"""
from __future__ import annotations

import json

from pipelines.core import Raw
from pipelines.core.http import fetch_raw

BASE = "https://api.mospi.gov.in/api"
PAGE = 100
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}


def month_period(year, month: str) -> str:
    """(2026, "September") -> "2026-09-01"."""
    return f"{int(year):04d}-{MONTHS[month]:02d}-01"


def pages(endpoint: str, params: dict) -> list[Raw]:
    """Fetch every page of one query; raises if the API returns an error body."""
    raws, page = [], 1
    while True:
        raw = fetch_raw(f"{BASE}/{endpoint}",
                        params={**params, "limit": PAGE, "page": page, "Format": "JSON"})
        body = json.loads(raw.content)
        if "data" not in body:
            raise RuntimeError(f"unexpected MoSPI {endpoint} response: {str(body)[:200]}")
        raws.append(raw)
        if page >= body["meta_data"]["totalPages"]:
            return raws
        page += 1


def rows(raws: list[Raw]) -> list[dict]:
    return [r for raw in raws for r in json.loads(raw.content)["data"]]
