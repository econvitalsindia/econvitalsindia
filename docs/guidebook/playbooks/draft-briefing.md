# Playbook: draft a briefing (Phase 3)

1. `python -m pipelines.briefings.ledger --product <daily|release|weekly> --date <YYYY-MM-DD>` writes `ledger.json`.
2. `python -m pipelines.briefings.draft --ledger ledger.json` makes an LLM draft that uses tokens only.
3. `python -m pipelines.briefings.check <draft.md>` must pass. If it fails, re-draft (max 2 retries), then hand over to a human.
4. Open a PR into `site/src/content/briefings/`. Put the cost and model in the PR body.
5. **Never merge it yourself.** A human reviews and merges.
