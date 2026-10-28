# Playbook: fix a broken scraper

**Input:** a `scraper-broken` issue. **Output:** a PR that restores the series, with a regression test.

1. Read the issue: series id, error, and the last successful fetch.
2. Reproduce locally: `make update SOURCE=<id>`.
   - 403 or timeout locally too (from India)? The site may be down. Wait one cycle and comment on the issue.
   - Works locally but fails in Actions? It's a foreign-IP block. Set `fetch: manual` in the yaml, update `03-data-sources.md`, and done.
3. Layout or URL change: save the new raw file as a fixture **next to** the old one (don't delete the old fixture).
4. Patch the parser so **both** fixtures parse. Add a test for the new fixture.
5. `make update SOURCE=<id>`. Confirm the CSV only gained new periods (or expected revisions).
6. PR with "Fixes #<issue>". Describe what changed at the source.

**Never:** hand-edit `data/series/*.csv`, loosen validation ranges just to get a pass, or delete fixtures.
