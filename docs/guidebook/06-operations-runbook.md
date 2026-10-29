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

**What goes out:** one email every morning at 07:30 IST (`newsletter-morning.yml`, cron `0 2 * * *` UTC): what is new in the data since the day before, markets, the wider picture, and what is due. `pipelines/newsletter/morning.py` writes it with Claude (`site.config.yaml → newsletter.llm_model`) from a ledger of facts built from the stored series (`registry/newsletter/morning.md → views`). The maintainer approved sending it without a person reading it first (2026-10-29), on these conditions:

- The model may only use the ledger's facts, and must write every number as a token (`{{cpi_headline_inflation.latest}}`). The briefing checker rejects any digit outside a token and any unknown token, so no number in the email is typed by the model.
- One retry with the checker's complaints. If that also fails, or the API errors, or `ANTHROPIC_API_KEY` is missing, the fixed template in `registry/newsletter/morning.md` is sent instead. The email always goes out.
- Every email is archived with its ledger in `data/newsletter/morning/<date>.md` and `.ledger.json`, and `data/newsletter/sent.json` stops a second send on the same day (so rerunning the workflow is safe).

**Cost (measured 2026-10-29):** about 12,000 input and 1,800 output tokens per email. On `claude-opus-5-5` ($4 / $20 per million tokens) that is about $0.08 a day, about $2.50 a month. On `claude-haiku-5-5` ($0.10 / $0.50) about $0.002 a day. Change `newsletter.llm_model` to switch.

**One-time setup (maintainer):**
1. Create a free Buttondown account (free for the first 100 subscribers; the plan assumes at most one email a day, which is what we send). Note your Buttondown username.
2. In Buttondown → Settings → API, copy the API key into a GitHub repo secret `BUTTONDOWN_API_KEY` (repo Settings → Secrets and variables → Actions). Never paste it into chat, issues or files.
3. From the Anthropic Console (console.anthropic.com → API keys), create a key and save it as the repo secret `ANTHROPIC_API_KEY`. Set a monthly spend limit in the Console as a safety net.
4. In `site.config.yaml`, set `newsletter.buttondown_username` and `newsletter.enabled: true`, then push. The signup box appears on the home and About pages; sign-ups confirm by email (double opt-in).
5. Subscribe yourself, confirm, then run the workflow by hand (Actions → newsletter-morning → Run workflow) and check the email arrives.

**Preview without sending:** `uv run python -m pipelines.newsletter.morning --preview /tmp/morning.md` (uses the AI if `ANTHROPIC_API_KEY` is set locally; add `--no-ai` for the template).

**The email went out as the template:** the workflow log says why ("attempt 1 rejected: ..." or "AI draft failed"). Repeated rejections usually mean the prompt needs a new rule (`SYSTEM` in morning.py), not a looser checker.

**The weekly digest** (`digest.py`, `newsletter.yml`) still exists but runs only by hand, as a Buttondown draft, because the morning email uses the free plan's one-email-a-day allowance.
