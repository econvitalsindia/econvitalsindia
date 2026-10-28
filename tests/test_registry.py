"""Registry and identity guard-rails run on every PR."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                          capture_output=True, text=True)


def test_registry_valid():
    r = run("validate_registry.py")
    assert r.returncode == 0, r.stdout


def test_site_name_only_in_config():
    r = run("check_name.py")
    assert r.returncode == 0, r.stdout


def test_every_auto_source_has_exactly_one_bot():
    import yaml
    from pipelines.core.store import ROOT
    from pipelines.run import discover, fetch_mode
    bots = yaml.safe_load((ROOT / "registry" / "bots.yaml").read_text())["bots"]
    assigned = [s for b in bots.values() for s in b["sources"]]
    sources = discover()
    assert len(assigned) == len(set(assigned)), "a source is in two bots"
    assert set(assigned) <= set(sources), f"unknown sources: {set(assigned) - set(sources)}"
    auto = {n for n, s in sources.items() if fetch_mode(s) == "auto"}
    assert auto - set(assigned) == set(), f"auto sources without a bot: {auto - set(assigned)}"
    assert not set(assigned) - auto, f"manual sources listed in a bot: {set(assigned) - auto}"
