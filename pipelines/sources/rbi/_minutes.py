"""Shared helpers for RBI's MPC minutes (press releases titled "Minutes of the Monetary Policy
Committee Meeting, <dates>", found through the press-release index, _press.releases)."""
from __future__ import annotations

import html
import re
from datetime import datetime

import pandas as pd

TITLE = "Minutes of the Monetary Policy Committee Meeting"
FIRST_MEETING = pd.Period("2016-10", freq="M")


def text_of(content: bytes) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", content.decode("utf-8", "ignore"))))


def meeting_period(text: str) -> str:
    """Month of the meeting's last day, from the title ('..., October 5 to 7, 2026' or
    '..., September 29 - October 1, 2025' or '... March 24, 26 and 27, 2020')."""
    m = re.search(TITLE + r",?\s*(.{0,60}?\d{4})", text)
    if not m:
        raise ValueError("no meeting dates in the title")
    words = m.group(1)
    month = re.findall(r"(January|February|March|April|May|June|July|August|September|October|November|December)", words)[-1]
    year = re.findall(r"\d{4}", words)[-1]
    return datetime.strptime(f"{month} {year}", "%B %Y").strftime("%Y-%m-01")


def vote_count(text: str) -> tuple[int, int] | None:
    """(for, against) on the first (rate) resolution, counted from its vote table
    ("Member Vote Dr. X Yes Dr.Y No ..."). Only the tally is kept, not who voted how."""
    i = text.find("Voting on the Resolution")
    j = text.find("Member Vote", i)
    if i < 0 or j < 0:
        return None
    block = re.split(r"Statement by|Voting on the Resolution", text[j + len("Member Vote"):])[0]
    votes = re.findall(r"\s*[A-Z][A-Za-z.'\- ]+?\s+(Yes|No)\b", block)
    return (votes.count("Yes"), votes.count("No")) if votes else None
