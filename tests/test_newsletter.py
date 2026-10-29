"""Newsletter digest: composed only from published briefings; never sends."""
from datetime import date

from pipelines.newsletter import digest


def test_compose_lists_week_and_footer(tmp_path, monkeypatch):
    for name, product, d in [("2026-10-26-cpi", "release-note", "2026-10-26"),
                             ("2026-10-31-weekly", "weekly-briefing", "2026-10-31"),
                             ("2026-10-30-daily", "daily-note", "2026-10-30"),
                             ("2026-10-20-iip", "release-note", "2026-10-20")]:
        (tmp_path / f"{name}.md").write_text(f"---\ntitle: T {name}\ndate: {d}\nproduct: {product}\n---\nBody of {name}.\n")
    monkeypatch.setattr(digest, "BRIEFINGS", tmp_path)
    cfg = digest.config()
    cfg["newsletter"]["products"] = ["weekly-briefing", "release-note"]
    subject, body = digest.compose(date(2026, 11, 1), cfg)
    assert subject == "T 2026-10-31-weekly"
    assert body.startswith("Body of 2026-10-31-weekly.")
    assert "2026-10-26-cpi" in body and "daily" not in body and "2026-10-20" not in body   # outside the week
    assert cfg["credit"]["inspired_by_url"] in body
    assert digest.compose(date(2026, 12, 1), cfg) is None


def test_no_key_means_no_request(monkeypatch, capsys):
    monkeypatch.delenv("BUTTONDOWN_API_KEY", raising=False)
    monkeypatch.setattr(digest, "create_draft", lambda *a: (_ for _ in ()).throw(AssertionError("called")))
    monkeypatch.setattr(digest, "compose", lambda on, cfg: ("s", "b"))
    monkeypatch.setattr("sys.argv", ["digest", "--date", "2026-11-01"])
    assert digest.main() == 0
    assert "nothing created" in capsys.readouterr().out


# --- Morning email (pipelines/newsletter/morning.py). The AI is faked: no API calls. ---
from pipelines.newsletter import morning


def fake_ai(drafts):
    """Return the given drafts in turn, as ai_draft would."""
    it = iter(drafts)
    return lambda ledger, new, model, feedback=None: (next(it), {"model": "fake", "input_tokens": 0,
                                                                  "output_tokens": 0, "stop_reason": "end_turn"})


def test_ai_draft_with_tokens_is_rendered(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(morning, "ai_draft", fake_ai(["**Prices.** CPI inflation was {{cpi_headline_inflation.latest}}."]))
    email = morning.compose(date(2026, 10, 29), morning.config())
    assert email["drafted_by"].startswith("AI")
    assert "{{" not in email["body"] and "%" in email["body"].split("\n")[0]      # the value, filled in
    assert "not typed by the AI" in email["body"]


def test_typed_number_is_rejected_then_retry_then_template(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    # Both drafts type a number: the checker rejects them and the template is used.
    monkeypatch.setattr(morning, "ai_draft", fake_ai(["Inflation was 5.5%.", "Still 5.5%."]))
    email = morning.compose(date(2026, 10, 29), morning.config())
    assert email["drafted_by"] == "template (no AI)"
    assert email["body"].startswith("**Markets.**") and "{{" not in email["body"]


def test_retry_can_fix_the_draft(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(morning, "ai_draft", fake_ai(["Repo at 5.50%.", "The repo rate is {{repo_rate.latest}}."]))
    assert morning.compose(date(2026, 10, 29), morning.config())["drafted_by"].startswith("AI")


def test_no_keys_means_nothing_sent(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("BUTTONDOWN_API_KEY", raising=False)
    monkeypatch.setattr(morning, "SENT", tmp_path / "sent.json")
    monkeypatch.setattr(morning, "send", lambda *a: (_ for _ in ()).throw(AssertionError("sent")))
    monkeypatch.setattr("sys.argv", ["morning", "--date", "2026-10-29"])
    assert morning.main() == 0
    assert "nothing sent" in capsys.readouterr().out


def test_fallback_template_passes_checker():
    from pipelines.briefings.check import body_of, problems
    front, text = morning.template()
    ledger, _ = morning.build_ledger(front, date(2026, 10, 29))
    assert problems(body_of(text), ledger.facts) == []
    assert problems("---\n---\n" + front["subject"], ledger.facts) == []
