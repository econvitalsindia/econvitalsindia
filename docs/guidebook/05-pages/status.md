# Status (internal until launch)

**Purpose:** Is every series fresh and every scraper healthy?

## Must include
- [x] Table of every series: last fetched, last new data, next expected release, stale/overdue/discontinued state, last error, fetch mode
- [x] Manual queue: `fetch: manual` series waiting on `make india-update`
- [x] Open `scraper-broken` and `large-revision` issues (via the gh CLI at build time)
- [ ] Actions minutes used this month vs the 2,000 free limit
- [x] Generated from `data/status.json`

## Must NOT include
- Secrets, tokens, or internal URLs with credentials

## Phase
2 (can be a plain table in Phase 1)
