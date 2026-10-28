# Playbook: add an indicator

**Input:** an indicator name or a `registry/backlog.yaml` entry. **Output:** a PR that passes `make check`.

1. `grep -ri "<concept>" registry/` to confirm it doesn't exist yet.
2. Read the source row in `docs/guidebook/03-data-sources.md`. If its status is `to-scout`, run `scout-source.md` first and update the row.
3. Choose the id per `04-adding-an-indicator.md` §3.
4. Copy `registry/series/_template.yaml` → `registry/series/<id>.yaml` and fill in **every** field. Leave `verified_against: []` for now.
5. Create or extend `pipelines/sources/<agency>/<dataset>.py` (subclass `pipelines.core.Source`; see the docstring there for the contract).
6. Fetch once and save a trimmed raw file to `tests/fixtures/<agency>/<dataset>/`.
7. Write `tests/sources/test_<agency>_<dataset>.py`. Pin **at least 3** values that you read from the official press release, not from our own output.
8. `make update SOURCE=<id>` and inspect the CSV (periods continuous? units right? latest period as expected?).
9. Verify the latest 2 values and one old value against the official release. Append to `verified_against` with `{url, checked_on, by}`.
10. Add the id to `registry/pages/<page>.yaml` and tick the line in `docs/guidebook/05-pages/<page>.md`.
11. Remove it from `registry/backlog.yaml`.
12. `make check`, then open the PR with the template. Say exactly which numbers you checked against which document.

**Stop and ask a maintainer if:** the licence is unclear, the source needs a login, or the values don't match the official release.
