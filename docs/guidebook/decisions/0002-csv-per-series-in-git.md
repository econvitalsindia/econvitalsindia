# 0002 · One CSV per series, committed to git

**Date:** 2026-10-28 · **Status:** accepted

**Decision:** `data/series/<id>.csv` with columns `period,value,vintage`, plus `data/meta/<id>.json`. Raw downloads are never committed; they are archived monthly as GitHub Release assets.
**Why:** revisions show as diffs in PRs, history comes free, there's no database to run, and files are small (most series are under 50 KB).
**Revisit if:** total `data/` exceeds about 200 MB, or daily series multiply. Then move to Parquet in Releases or Cloudflare R2.
