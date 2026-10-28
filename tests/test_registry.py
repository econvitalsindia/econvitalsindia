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
