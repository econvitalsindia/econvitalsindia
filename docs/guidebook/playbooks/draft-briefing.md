# Playbook: draft a briefing

Release notes (live):
1. `make briefings` (or `uv run python -m pipelines.briefings.draft --date YYYY-MM-DD`) drafts every template whose trigger series got a new observation that day. Use `--force cpi gdp` to draft specific templates.
2. Drafts land in `site/src/content/briefings/` and their ledgers in `data/briefings/`. Read them; never edit a number by hand. If wording is wrong, fix the **template** (`registry/briefings/`) and redraft.
3. On GitHub the `briefing` workflow does this automatically and opens a pull request. **Never merge it yourself as an agent**; a person reviews and merges.

New template:
1. Copy an existing `registry/briefings/*.md`, set `trigger` and `views`.
2. No digits in the body, only tokens. Facts are listed in `pipelines/briefings/ledger.py`.
3. `uv run python -m pipelines.briefings.draft --check-only`, then `--force <name>` to read the output. Move the test output out of the repo before committing (it must reach `main` only via a reviewed PR).
