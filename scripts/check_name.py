"""Fail if the site name appears anywhere except site.config.yaml.

The name lives only in site.config.yaml so the site can be renamed by
editing one file (docs/guidebook/09-rebranding.md).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
# Historical records may name the site; everything else must not.
EXEMPT = {"site.config.yaml"}
EXEMPT_DIRS = ("docs/guidebook/decisions/",)


def tracked_files() -> list[str]:
    """Return files git knows about (tracked or untracked, not ignored)."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [f for f in out.stdout.splitlines() if f]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--also", action="append", default=[],
                        help="extra name to forbid (e.g. the old name after a rename)")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / "site.config.yaml").read_text())
    names = [config["site"]["name"], *args.also]
    pattern = re.compile("|".join(re.escape(n) for n in names), re.IGNORECASE)

    hits = []
    for rel in tracked_files():
        if rel in EXEMPT or rel.startswith(EXEMPT_DIRS):
            continue
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{rel}:{lineno}: {line.strip()}")

    if hits:
        print("Site name hard-coded outside site.config.yaml:")
        print("\n".join(hits))
        return 1
    print(f"name check ok ({', '.join(names)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
