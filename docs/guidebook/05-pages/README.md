# 05 · Page checklists

One file per page. Every file uses the same sections:

- **Purpose**: the question the page answers, in one or two sentences.
- **Must include**: a checklist. Tick `[x]` when it is live and verified, and note the PR number.
- **Must NOT include**: the guard-rails.
- **Series**: ids from `registry/series/` (planned ids are in `registry/backlog.yaml`).
- **Layout and charts**: section order and chart types.
- **Done when**: the acceptance test for the page.
- **Phase**: when it is built.

The machine-readable twin of each file is `registry/pages/<page>.yaml`. When they disagree, fix the yaml to match this file, or update this file in the same PR.

| Page | File | Phase |
|---|---|---|
| Home dashboard | home.md | 1 |
| Growth | growth.md | 2 |
| Inflation | inflation.md | 2 |
| Jobs | jobs.md | 2 |
| Activity | activity.md | 2 |
| Money & banking | money-banking.md | 2 |
| Markets | markets.md | 2 |
| Fiscal | fiscal.md | 2 |
| External | external.md | 2 |
| States | states.md | 4 |
| Calendar | calendar.md | 1 |
| Briefings | briefings.md | 3 |
| Data & Methods | data-methods.md | 2 |
| About | about.md | 1 |
| Status (internal) | status.md | 2 |
| Tools (index) | tools.md | 4 |
