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

## A published value looks wrong

Sometimes a publisher's feed carries an obvious error, e.g. a value attached to the wrong period. Don't edit the CSV. Add an `exclude` entry to the series yaml: `{period, added, reason}`, with the evidence in `reason`. The value is then never published, and the series page shows it under "Values left out". Report it to the publisher if possible, and remove the entry once they fix the feed. Example: `plfs_ur_quarterly_urban`, April–June 2019.

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
- Refresh `registry/calendar/` from the official calendars (MoSPI ARC, OEA ICI/WPI ARC, RBI MPC schedule, Commerce SDDS calendar). Check the coming month's dates for public holidays (the build only shifts weekends) and confirm any `estimated: true` dates you can. Extend each file so it always covers at least the next three months. At the start of each financial year, add the new ARC files and MPC schedule.

## Secrets

Kept in GitHub Actions secrets only: `LLM_API_KEY`, `NEWSLETTER_API_KEY`, `CLOUDFLARE_API_TOKEN`. Never in code, the registry, issues or chat logs.

## Newsletter

A weekly digest goes out by email: the latest weekly briefing plus links to that week's release and MPC notes. Daily notes are left out. `pipelines/newsletter/digest.py` builds it from briefings already on `main`, so it carries nothing that hasn't been reviewed. The `newsletter.yml` workflow (Sunday 10:00 IST) creates it as a **draft** in Buttondown. A person reads it there and presses send. Nothing in this repo sends email, and subscriber addresses live only with the provider.

**Why not Buttondown's RSS-to-email?** It is a paid add-on (+$9/month, checked 28 Oct 2026). Our workflow does the same job for free through the API.

**One-time setup (maintainer):**
1. Create a free Buttondown account (free up to 100 subscribers). Under Settings → API, check that the API is available on the free plan; we could not confirm this from their public pages.
2. Copy the API key into a GitHub repo secret named `BUTTONDOWN_API_KEY` (Settings → Secrets and variables → Actions). Never paste it into chat, issues or files.
3. From Buttondown's embed-form settings, copy the form's `action` URL into `site.config.yaml` → `newsletter.signup_action`. The form must post a field named `email`; check the embed code.
4. Set `newsletter.enabled: true` and push. The signup box then appears on the home and briefings pages.
5. Run the `newsletter` workflow by hand once (Actions → newsletter → Run workflow) and check that the draft appears in Buttondown.

**Preview without an account:** `uv run python -m pipelines.newsletter.digest --preview /tmp/digest.md`.

**A draft appears twice:** `data/newsletter/drafted.json` records each drafted date, and the workflow commits it. If the commit failed, delete the duplicate in Buttondown.
