"""Probe every portal in registry/probe_targets.yaml and report reachability.

Run it from India (`python scripts/probe_sources.py --label india`) and from
GitHub Actions (probe-sources workflow, label `actions-us`). A portal that
works from India but not from Actions should use `fetch: manual`.
Results are written to data/probes/<label>.json.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}


def probe(url: str) -> dict:
    """Fetch one URL and summarise the response (no retries: we want the raw truth)."""
    start = time.monotonic()
    try:
        r = httpx.get(url, headers=HEADERS, timeout=25, follow_redirects=True)
        return {"status": r.status_code, "final_url": str(r.url),
                "content_type": r.headers.get("content-type", ""),
                "bytes": len(r.content), "seconds": round(time.monotonic() - start, 1),
                "error": None}
    except httpx.HTTPError as e:
        return {"status": None, "final_url": None, "content_type": "", "bytes": 0,
                "seconds": round(time.monotonic() - start, 1),
                "error": f"{type(e).__name__}: {e}"[:200]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="where this ran, e.g. india or actions-us")
    args = parser.parse_args()

    targets = yaml.safe_load((ROOT / "registry" / "probe_targets.yaml").read_text())["targets"]
    results = {}
    for t in targets:
        results[t["name"]] = {"url": t["url"], **probe(t["url"])}
        res = results[t["name"]]
        print(f"{t['name']:<16} {str(res['status']):<5} {res['bytes']:>9}B {res['seconds']:>5}s "
              f"{res['error'] or ''}")
        time.sleep(1)  # be polite to government servers

    out = ROOT / "data" / "probes" / f"{args.label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"label": args.label,
                               "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "results": results}, indent=2))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
