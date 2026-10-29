"""MPC decisions: the policy repo rate after each meeting, the stance, and the meeting dates.

Read from the same RBI minutes as MPC Speak (mpc_minutes.py). The resolution near the top
says what the committee decided:
  "... decided to: • reduce the policy repo rate under the liquidity adjustment facility (LAF)
   by 25 basis points from 6.50 per cent to 6.25 per cent"
  "... voted unanimously to keep the policy repo rate ... unchanged at 5.50 per cent"
The rate is the last "N.NN per cent" in that sentence. The stance is the last stance word
in the first sentence about the stance ("change the stance from neutral to accommodative"
gives accommodative); when the minutes don't state it, the previous meeting's stance holds.

Since 2025 the vote table also records the size each member voted for ("Magnitude of policy
repo rate reduction (basis points)"); members who voted Yes but for a different size are
noted, since the Yes/No vote alone hides that split.

Also RBI's projections for the financial year, from the same resolution text:
  mpc_cpi_projection, mpc_gdp_projection   value = % for the year; note: "for 2026-27"

One series, period = month of the meeting, value = repo rate after the decision:
  mpc_repo_decision   note: "<meeting dates>; stance: <stance>[; size: <who wanted what>]"
The vote split comes from mpc_member_dissent; the change from the previous meeting's rate.
"""
from __future__ import annotations

import re

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw
from pipelines.core.store import load_series
from pipelines.sources.rbi._press import RELEASE, releases
from pipelines.sources.rbi.mpc_minutes import FIRST_MEETING, TITLE, meeting_period, text_of

DECISION = re.compile(r"(?:decided|voted)[^•]{0,40}?to:?\s*•?\s*(reduce|cut|increase|raise|keep|maintain|retain)"
                      r"\s+the policy repo rate", re.I)
# The new rate: "... to 6.25 per cent", "unchanged at 6.50 per cent", "at 5.50 per cent"
# (not "from 6.50 per cent").
RATE = re.compile(r"\b(?:at|to)\s+(\d{1,2}(?:\.\d{1,2})?)\s*per cent", re.I)
STANCES = ["withdrawal of accommodation", "calibrated tightening", "accommodative", "neutral"]
# Sentences split on full stops that are not decimal points.
SENTENCE = re.compile(r"(?<!\d)\.(?!\d)")
RESOLUTION_END = re.compile(r"main considerations|Assessment|Statement by")


def meeting_dates(text: str) -> str:
    """'October 5 to 7, 2026' (as printed in the title)."""
    m = re.search(TITLE + r",?\s*(.{0,60}?\d{4})", text)
    return m.group(1).strip() if m else ""


def decision(text: str) -> tuple[float, str | None]:
    """(repo rate after the meeting, stance or None) from the resolution."""
    m = DECISION.search(text)
    if not m:
        raise ValueError("no rate resolution found")
    rate = RATE.search(text, m.end(), m.end() + 300)
    if not rate:
        raise ValueError("no new repo rate in the resolution")
    # The resolution runs from the decision to "The main considerations ..." / "Assessment".
    end = RESOLUTION_END.search(text, m.end())
    block = text[m.start(): min(end.start() if end else len(text), m.end() + 2500)]
    stance = stance_in(block, r"stance|remain|focus")
    if stance is None:
        # Since 2025 the stance decision follows the outlook ("Hence, the MPC also decided to
        # change the stance from accommodative to neutral"), still before the statements.
        stop = text.find("Statement by", m.end())
        stance = stance_in(text[m.end(): stop if stop > 0 else None], r"decided.*stance")
    return float(rate.group(1)), stance


def size_split(text: str) -> str:
    """'1 member voted for 25 bp' when members voted Yes for different sizes of the move."""
    i = text.find("Voting on the Resolution")
    j = text.find("Magnitude of policy repo rate", i)
    if i < 0 or j < 0 or j - i > 300:
        return ""
    block = re.split(r"Statement by|Voting on the Resolution", text[j:])[0]
    sizes = [int(b) for b in re.findall(r"\b(?:Yes|No)\s+(\d{1,3})\b", block)]
    if len(set(sizes)) < 2:
        return ""
    majority = max(set(sizes), key=sizes.count)
    others = sorted({b for b in sizes if b != majority})
    return "; ".join(f"{sizes.count(b)} member{'s' if sizes.count(b) > 1 else ''} voted for {b} bp"
                     for b in others)


def stance_in(block: str, cue: str) -> str | None:
    """The stance in the first sentence that names one and matches `cue`."""
    for sentence in SENTENCE.split(block):
        low = sentence.lower()
        words = [(low.rfind(w), w) for w in STANCES if w in low]
        if words and re.search(cue, low):
            # "change the stance from neutral to accommodative": the last word is the new stance.
            return max(words)[1]
    return None


# Projections in the resolution: "CPI inflation for 2026-27 is projected at 4.6 per cent with
# Q1 at ...", "real GDP growth for 2025-26 has been retained at 6.5 per cent", "CPI inflation
# is projected to be 5.2 per cent for 2026-27". Quarter figures ("Q1:2027-28") are skipped.
FY = re.compile(r"(?<![Q\d]:)(?<!:)\b(20\d\d-\d\d)\b")
PROJECTED = re.compile(r"(?:projected|retained|revised)[^%]{0,60}?(?:at|to be|to)\s+(\d{1,2}\.\d) per cent")


def projection(head: str, subject: str) -> tuple[str, float] | None:
    """(financial year, %) from the first sentence about `subject` ("CPI inflation" or
    "GDP growth") that projects a whole financial year."""
    for sentence in SENTENCE.split(head):
        if subject.lower() not in sentence.lower() or "core" in sentence.lower():
            continue
        years = [y for y in FY.findall(sentence) if not re.search(rf"Q\d\s*:\s*{y}", sentence)]
        value = PROJECTED.search(sentence)
        if years and value:
            return years[0], float(value.group(1))
    return None


class MpcDecisions(Source):
    name = "rbi_mpc_decisions"
    series_ids = ("mpc_repo_decision", "mpc_cpi_projection", "mpc_gdp_projection")

    def fetch(self) -> list[Raw]:
        rescan = len(load_series("mpc_repo_decision")) < 20
        months = (pd.Period.now(freq="M") - FIRST_MEETING).n + 1 if rescan else 4
        found = releases(lambda t: t.startswith(TITLE), months)
        if not found:
            raise RuntimeError(f"no MPC minutes in the last {months} months of the RBI press index")
        return [fetch_raw(RELEASE.format(prid=p), suffix=".html") for p in sorted(found)]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        rows, proj = [], []
        for raw in raws:
            text = text_of(raw.content)
            period = meeting_period(text)
            stop = text.find("Statement by")
            head = text[:stop if stop > 0 else None]
            for sid, subject in (("mpc_cpi_projection", "CPI inflation"), ("mpc_gdp_projection", "GDP growth")):
                found = projection(head, subject)
                if found:
                    proj.append({"series_id": sid, "period": period, "value": found[1], "note": f"for {found[0]}"})
            rate, stance = decision(text)
            rows.append({"period": meeting_period(text), "value": rate,
                         "dates": meeting_dates(text), "stance": stance, "size": size_split(text)})
        df = pd.DataFrame(rows).drop_duplicates("period", keep="last").sort_values("period")
        # Minutes that don't restate the stance keep the previous one. A partial fetch (the
        # last four months) starts from the stance already stored.
        stored = load_series("mpc_repo_decision")
        before = stored[stored["period"] < df["period"].min()]
        start = before["note"].iloc[-1].split("stance: ")[-1].split(";")[0] if len(before) else None
        df["stance"] = df["stance"].ffill().fillna(start).fillna("not stated")
        df["note"] = df["dates"] + "; stance: " + df["stance"] + df["size"].map(lambda x: f"; size: {x}" if x else "")
        df["series_id"] = "mpc_repo_decision"
        out = df[["series_id", "period", "value", "note"]]
        if proj:
            out = pd.concat([out, pd.DataFrame(proj).drop_duplicates(["series_id", "period"], keep="last")])
        return out


SOURCE = MpcDecisions()
