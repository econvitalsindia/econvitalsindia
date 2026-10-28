# 07 · Editorial policy (briefings and newsletter)

## Principles

1. **AI drafts, a person approves.** Every briefing is opened as a PR by `briefing.yml`. Only a human merge publishes it and sends the email. Agents never merge briefing PRs.
2. **The model never types a number.** Numbers come from a **ledger** and nothing else.
3. **Only our data plus official releases.** Context comes from our series and from official press releases (RBI, MoSPI, PIB, ministries). No news scraping, rumours or paywalled research in Phase 3.
4. **Say who wrote it.** "Drafted by AI from the site's data; reviewed by <role>", or "Written by <name>".

## The ledger

For each briefing, `pipelines/briefings/ledger.py` builds `ledger.json`. Each entry looks like:

```json
{"key": "cpi.headline.yoy.latest", "series_id": "cpi_headline_index", "transform": "yoy",
 "period": "2026-09-01", "value": 3.7, "display": "3.7%", "source_url": "...", "vintage": "2026-10-12"}
```

The draft uses tokens: `Headline inflation was {{cpi.headline.yoy.latest}} in {{cpi.headline.period.latest}}.` The build resolves them.

**Checker (`pipelines/briefings/check.py`) fails the draft if:**
- any digit appears in prose outside a token (allow-list: years, dates, "Q1", "FY27", "MPC's 4% target" → use tokens for targets too),
- a token isn't in the ledger,
- a comparative word ("rose", "fell", "highest since") contradicts the ledger values (e.g. "rose" while the value fell).

## Tone

Plain and precise. Lead with what changed and why it matters. One idea per paragraph. No forecasts of our own unless they are tagged Originals. No policy advocacy.

## Reviewer checklist (on the PR)

- [ ] Checker passed (CI)
- [ ] Spot-check 3 numbers against the press release
- [ ] No claims beyond the data and official text
- [ ] Headline is accurate, not sensational
- [ ] Charts render

## Corrections

Fix the source of the error (data or prompt), not just the text. Add a dated "Correction:" line at the bottom of the published item. If it was emailed, include a correction note in the next edition.

## Cost control

The model is set in `site.config.yaml → briefings.llm_model`. Before choosing, benchmark at least two models (one cheap) on 10 past releases and compare checker pass rate, reviewer edits and cost. Log the cost per draft in the PR body.
