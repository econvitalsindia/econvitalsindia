"""Open or update one `scraper-broken` GitHub issue per failed series (used by workflows).

Reads data/raw/last_run.json written by pipelines.run. Needs the `gh` CLI and GH_TOKEN.
Issues are titled "scraper-broken: <series_id>" so repeat failures comment on the same issue.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main() -> None:
    report = json.loads((ROOT / "data/raw/last_run.json").read_text())
    run_url = os.environ.get("RUN_URL", "")
    for f in report["failures"]:
        title = f"scraper-broken: {f['series_id']}"
        body = (f"Source `{f['source']}` failed for `{f['series_id']}` at {report['at']}.\n\n"
                f"```\n{f['error'][:1500]}\n```\n\n{run_url}\n\n"
                "Fix with docs/guidebook/playbooks/fix-scraper.md. The site keeps the last good values.")
        existing = json.loads(gh("issue", "list", "--state", "open", "--label", "scraper-broken",
                                 "--search", f'"{title}" in:title', "--json", "number,title"))
        match = next((i for i in existing if i["title"] == title), None)
        if match:
            gh("issue", "comment", str(match["number"]), "--body", body)
            print(f"commented on #{match['number']} {title}")
        else:
            gh("issue", "create", "--title", title, "--label", "scraper-broken", "--body", body)
            print(f"opened issue: {title}")


if __name__ == "__main__":
    main()
