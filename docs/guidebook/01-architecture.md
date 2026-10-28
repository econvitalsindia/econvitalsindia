# 01 · Architecture

## Data flow

```
sources (MoSPI, RBI, CGA, Commerce, NSDL, AMFI, Grid-India, NPCI, Yahoo, …)
   │  GitHub Actions cron (IST)        +  `make india-update` from a machine in India
   ▼
pipelines/sources/<agency>/<dataset>.py
   fetch()    → raw bytes + receipt (url, fetched_at, sha256)  → data/raw/ (git-ignored) → Release asset
   parse()    → tidy frame: period, value, series_id, vintage
   validate() → schema, plausible range, no silent gaps, revision diff vs stored series
   publish()  → data/series/<id>.csv + data/meta/<id>.json + data/status.json
   ▼
pipelines/build/  → site/src/data/*.json (per page, per chart)
   ▼
site/ (Astro, static, Observable Plot) → Cloudflare Pages (private preview behind Cloudflare Access)
```

## Why this stack (details in `decisions/`)

- **Static site.** Free, fast, nothing to keep alive. All computation happens at build time.
- **Astro.** Markdown content collections handle briefings and blog posts. Components are simple enough for RAs.
- **Observable Plot.** Economist-style charts with very little code.
- **CSV per series in git.** Revisions show up as diffs in PRs and history is free. Raw files stay out of git.
- **Python 3.12 + uv** for pipelines.
- **Cloudflare Pages.** Serves a *private* repo for free, and Cloudflare Access gates the preview. GitHub Pages on a free org needs a public repo.

## The registry is the spine

Everything reads from `registry/`:

- `registry/series/<id>.yaml` holds the indicator metadata (schema: `registry/series/_schema.md`, template: `_template.yaml`).
- `registry/pages/<page>.yaml` lists a page's sections, their series and chart types.
- `registry/calendar/<publisher>.yaml` holds the expected release dates.

Pages, the calendar, the Data & Methods page, freshness checks and the briefing ledger are all generated from it. **If it isn't in the registry, it doesn't exist.**

## Failure handling

A source that fails to fetch, parse or validate:

1. leaves `data/series/<id>.csv` untouched,
2. sets `stale: true` and `last_error` in `data/status.json`,
3. opens or updates one GitHub issue per series, labelled `scraper-broken`,
4. shows on the internal Status page.

Revisions that move a past value by more than the series' `revision_alert` threshold also open an issue, labelled `large-revision`. They do not block publishing.

## Schedules (all IST; Actions cron is written in UTC)

| Workflow | When (IST) | Does |
|---|---|---|
| `markets.yml` | Mon–Fri 17:00 | Index levels, USD/INR, G-sec, crude, gold |
| `daily.yml` | Daily 18:30 | Today's calendar releases + a sweep of all `fetch: auto` series |
| `rbi-weekly.yml` | Fri 19:30 | RBI weekly statistical supplement, FX reserves, bank credit (fortnightly) |
| `healthcheck.yml` | Daily 08:00 | Lists overdue series vs calendar, opens issues |
| `build.yml` | On push to `main` | Build + deploy |
| `briefing.yml` | Weekday 19:30 + after major releases | Drafts the briefing PR (Phase 3) |

**Free-tier budget.** A private repo gets 2,000 Action-minutes a month, and the planned load is about 600–900. Track actual use on the Status page. Public repos (after launch) are unlimited.

## The foreign-IP fallback

GitHub-hosted runners are in the US. NSE, CCIL and some gov.in portals often block them. Every series yaml says `fetch: auto` or `fetch: manual`:

- `auto` runs in Actions.
- `manual` runs with `make india-update` on any machine in India. It runs all manual sources, validates them, commits on a branch, and opens a PR. Expected cadence is once per working day, about 5 minutes.

When an `auto` source starts failing with 403s or timeouts from Actions but works from India, flip it to `manual` and note it in `03-data-sources.md`. A later free upgrade is to register an always-on Mac as a **self-hosted runner**, which runs `manual` sources on a schedule.

## What makes us different from econvitals

1. **States**: a state dashboard with choropleths (GSDP, state CPI, PLFS unemployment, state finances).
2. **MPC Speak**: hawk–dove scoring of *each MPC member's* statement in the RBI minutes.
3. **Base-year bridge**: properly linked long series across the 2026 rebasing (GDP 2022-23, CPI 2024, IIP 2022-23).
4. **Monsoon and food watch**: IMD rainfall vs normal, reservoir storage, vegetable prices next to CPI food.
5. **Digital pulse**: UPI, FASTag and e-way bills as high-frequency activity indicators.
6. **Indian conventions**: FY quarters, ₹ lakh crore, crore ↔ billion toggle.
7. **Citable and downloadable**: every chart has CSV download and a "cite this" line (.dta later).
8. **Built for more than one language**: no hard-coded UI strings, so a Hindi version is possible later.
