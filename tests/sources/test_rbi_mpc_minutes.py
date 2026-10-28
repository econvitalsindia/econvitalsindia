"""MPC minutes: statement splitting, votes and scoring (MPC Speak)."""
import re

from pipelines.sources.rbi.mpc_minutes import (load_lexicon, meeting_period, parse_minutes, rate_votes,
                                               statements, text_of, tone)
from tests.conftest import FIXTURES


def text(month: str) -> str:
    return text_of((FIXTURES / "rbi" / f"mpc_minutes_{month}.html").read_bytes())


def test_february_2025_title_variants():
    x = text("2025-02")           # "Prof Ram Singh" (no dot), "M. Rajeshwar Rao" (no title)
    assert meeting_period(x) == "2025-02-01"
    votes = rate_votes(x)
    assert len(votes) == 6 and "Ram Singh" in votes and "M. Rajeshwar Rao" in votes
    assert set(statements(x, list(votes))) == set(votes)


def test_june_2017_dissent_and_spacing():
    x = text("2017-06")           # "Dr.Pami Dua" (no space); Dholakia voted No
    votes = rate_votes(x)
    assert votes == {"Chetan Ghate": 0, "Pami Dua": 0, "Ravindra H. Dholakia": 1,
                     "Michael Debabrata Patra": 0, "Viral V. Acharya": 0, "Urjit R. Patel": 0}
    rows = parse_minutes(x, load_lexicon())
    assert sum(r["series_id"] == "mpc_member_tone" for r in rows) == 6


def test_score_formula_and_whole_words():
    lex = load_lexicon()
    assert tone("We must remain vigilant.", lex) == (1 / 3, 1, 0)
    assert tone("Downside risks to growth; support growth.", lex) == (-2 / 4, 0, 2)
    assert tone("Nothing relevant here.", lex) == (0.0, 0, 0)
    assert tone("The slackness of the rope", lex)[1:] == (0, 0)   # 'slack' needs a word boundary
    for side in ("hawkish", "dovish"):
        assert all(isinstance(p, re.Pattern) for p in lex[side])
