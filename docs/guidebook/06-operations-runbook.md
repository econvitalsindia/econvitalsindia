# 06 · Operations runbook

## Daily routine (about 10 minutes, one person)

1. **Morning (by 10:00 IST):** open the Status page. Triage any new `scraper-broken` issue: assign it, or fix it with `playbooks/fix-scraper.md`.
2. **Evening (after 19:00 IST):** run `make india-update` from a machine in India. It opens a PR. Check the diff (new periods only, or revisions?) and merge.
3. **If a briefing PR is open:** review and merge it (see `07-editorial-policy.md`). Unmerged drafts expire after 24 h.

## Release days

For CPI, GDP, IIP, PLFS, the MPC decision and trade, follow `playbooks/release-day.md`. In short: confirm the series updated, eyeball the chart, spot-check against the press release, then review the release-note PR.

## When a scraper breaks

- The data on the site stays at the last good value and the series shows a stale badge. **Nothing is broken publicly**, just late.
- Typical causes: the agency changed the file layout, the URL pattern changed, a foreign-IP block, or the site is down.
- If the site is just down, wait one cycle. If the layout changed, follow `playbooks/fix-scraper.md`, using the archived raw file as a new fixture.

## Revisions

Revisions are normal (GDP, IIP, EPFO revise often). The pipeline stores every vintage. Revisions above a series' `revision_alert` open a `large-revision` issue. Confirm against the press release and close it. Don't "fix" revisions by hand.

## Base-year changes

When an agency rebases (as in 2026 for GDP, CPI and IIP):
1. Create new series ids for the new base and keep the old ones (mark them `discontinued: <date>`).
2. Build or refresh `<id>_linked` using the documented splice method.
3. Point pages at the new or linked ids, and add a note on the page.

## Manual queue etiquette

- Run it from India, on a normal residential or office connection.
- Don't run it more than twice a day (be polite to government servers).
- Each manual source has a 5-second delay between requests (set in `pipelines/core/http.py`).

## Monthly

- Check the Actions minutes used (Status page).
- Archive `data/raw/` from the month as a GitHub Release asset (`make archive-raw`).
- Refresh `registry/calendar/` from any new published calendars (MoSPI ARC updates, the RBI MPC schedule).

## Secrets

Kept in GitHub Actions secrets only: `LLM_API_KEY`, `NEWSLETTER_API_KEY`, `CLOUDFLARE_API_TOKEN`. Never in code, the registry, issues or chat logs.
