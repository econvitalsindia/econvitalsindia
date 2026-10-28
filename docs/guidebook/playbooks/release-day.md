# Playbook: release day

**Input:** a calendar release (e.g. CPI, 12th, 16:00 IST). **Output:** updated series and a release-note PR.

1. After the release time, run `make update SOURCE=<id>` for the release's series (or wait for the bot that owns it, see `registry/bots.yaml`; or run that bot by hand: Actions → `<name>-bot` → Run workflow).
2. Open the press release. Check the headline and 2 components against `data/series`.
3. Check the page chart renders and the home tile updated.
4. Phase 3+: `briefing.yml` opens a release-note PR. Review it with `07-editorial-policy.md`'s reviewer checklist and merge.
5. If the numbers disagree: **do not publish**. Open an issue and tag the maintainer.
