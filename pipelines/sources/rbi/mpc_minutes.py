"""MPC Speak: tone of each MPC member's statement in the RBI minutes, and their rate vote.

Minutes are RBI press releases titled "Minutes of the Monetary Policy Committee Meeting,
<dates>", found through the press-release index (_press.releases). Each has a vote table
("Voting on the Resolution to ... policy repo rate ... Member Vote Dr. X Yes ...") and one
"Statement by <title> <Name>" section per member, ending at the signature line
("(Name) Chief General Manager").

Two panels (entity = member, period = month of the meeting):
  mpc_member_tone     (hawkish - dovish) / (hawkish + dovish + 2) phrase counts, between -1
                      and +1; the +2 pulls statements with few matching phrases towards 0
                      (one phrase alone scores +/-0.33, not +/-1). Lexicon:
                      registry/mpc/lexicon.yaml
  mpc_member_dissent  1 if the member voted No on the rate resolution, else 0
No language model is involved: the score is reproducible from the text and the lexicon.
"""
from __future__ import annotations

import html
import os
import re
from datetime import datetime

import pandas as pd
import yaml

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import ROOT, load_panel
from pipelines.sources.rbi._press import RELEASE, releases

LEXICON = ROOT / "registry" / "mpc" / "lexicon.yaml"
TITLE = "Minutes of the Monetary Policy Committee Meeting"
FIRST_MEETING = pd.Period("2016-10", freq="M")
TITLE_RE = r"(?:Dr|Shri|Smt|Prof)\.?\s*"            # "Dr.", "Dr.Pami", "Prof", or none at all
SIGNATURE = re.compile(r"\(\s*[A-Z][A-Za-z.\s]{2,40}\)\s*(?:Chief General Manager|General Manager|Deputy General Manager|Adviser|Director)")


def text_of(content: bytes) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", content.decode("utf-8", "ignore"))))


def clean_name(name: str) -> str:
    """'Dr. Michael Debabrata Patra' -> 'Michael Debabrata Patra' (titles change; people don't)."""
    return re.sub(rf"^{TITLE_RE}", "", name.strip()).strip()


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


def rate_votes(text: str) -> dict[str, int]:
    """{member: 1 if No on the first (rate) resolution, else 0}, from its vote table
    ("Member Vote Dr. X Yes Dr.Y No M. Z Yes ...")."""
    i = text.find("Voting on the Resolution")
    j = text.find("Member Vote", i)
    if i < 0 or j < 0:
        return {}
    block = re.split(r"Statement by|Voting on the Resolution", text[j + len("Member Vote"):])[0]
    return {clean_name(n): int(v == "No") for n, v in re.findall(r"\s*([A-Z][A-Za-z.'\- ]+?)\s+(Yes|No)\b", block)}


def statements(text: str, members: list[str]) -> dict[str, str]:
    """{member: statement text}. Each "Statement by" section is assigned to the member (from
    the vote table) whose name follows it; titles and spacing vary too much to parse."""
    marks = [m.end() for m in re.finditer(r"Statement by", text)]
    out = {}
    for k, start in enumerate(marks):
        end = marks[k + 1] - len("Statement by") if k + 1 < len(marks) else len(text)
        head = re.sub(r"\s", "", text[start:start + 80]).lower()
        member = next((m for m in members if re.sub(r"\s", "", m).lower() in head), None)
        if member is None:
            continue
        sig = SIGNATURE.search(text, start, end)
        out[member] = text[start:sig.start() if sig else end]
    return out


def load_lexicon() -> dict[str, list[re.Pattern]]:
    lex = yaml.safe_load(LEXICON.read_text())
    return {side: [re.compile(rf"\b{p}\b", re.I) for p in lex[side]] for side in ("hawkish", "dovish")}


def tone(statement: str, lexicon: dict[str, list[re.Pattern]]) -> tuple[float, int, int]:
    h = sum(len(p.findall(statement)) for p in lexicon["hawkish"])
    d = sum(len(p.findall(statement)) for p in lexicon["dovish"])
    return (h - d) / (h + d + 2), h, d


def parse_minutes(text: str, lexicon) -> list[dict]:
    period = meeting_period(text)
    votes = rate_votes(text)
    rows = []
    for member, body in statements(text, list(votes)).items():
        score, h, d = tone(body, lexicon)
        rows.append({"series_id": "mpc_member_tone", "entity": member, "period": period,
                     "value": round(score, 3), "note": f"{h} hawkish, {d} dovish phrases"})
    for member, no in votes.items():
        rows.append({"series_id": "mpc_member_dissent", "entity": member, "period": period, "value": no, "note": ""})
    return rows


class MpcMinutes(Source):
    name = "rbi_mpc_minutes"
    panel = True
    series_ids = ("mpc_member_tone", "mpc_member_dissent")

    def fetch(self) -> list[Raw]:
        # MPC_RESCAN=1 re-reads every meeting since 2016 (after a lexicon change).
        have = load_panel("mpc_member_tone")
        rescan = os.environ.get("MPC_RESCAN") == "1" or have["period"].nunique() < 20
        months = (pd.Period.now(freq="M") - FIRST_MEETING).n + 1 if rescan else 4
        found = releases(lambda t: t.startswith(TITLE), months)
        if not found:
            raise RuntimeError(f"no MPC minutes in the last {months} months of the RBI press index")
        return [fetch_raw(RELEASE.format(prid=p), suffix=".html") for p in sorted(found)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        lexicon = load_lexicon()
        rows = []
        for raw in raws:
            rows += parse_minutes(text_of(raw.content), lexicon)
        return pd.DataFrame(rows)


SOURCE = MpcMinutes()
