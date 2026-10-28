"""RBI press-release index: find releases by title.

The index (https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx) is an ASP.NET
form. POSTing its hidden fields with hdnYear/hdnMonth returns that month's list.
"""
from __future__ import annotations

import re

import httpx
import pandas as pd

from pipelines.core.http import HEADERS

INDEX = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
RELEASE = "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid={prid}"


def releases(title_test, months: int) -> dict[str, str]:
    """{prid: title} for releases in the last `months` months whose title passes title_test."""
    found: dict[str, str] = {}
    with httpx.Client(headers=HEADERS, timeout=60, follow_redirects=True) as client:
        for p in pd.period_range(end=pd.Period.now(freq="M"), periods=months, freq="M"):
            page = client.get(INDEX).text
            fields = dict(re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', page))
            fields.update({"hdnYear": str(p.year), "hdnMonth": str(p.month)})
            html = client.post(INDEX, data=fields).text
            for prid, title in re.findall(r"href=['\"]?BS_PressReleaseDisplay\.aspx\?prid=(\d+)['\"]?>([^<]+)</a>", html):
                if title_test(title.strip()):
                    found[prid] = title.strip()
    return found
