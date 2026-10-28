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
