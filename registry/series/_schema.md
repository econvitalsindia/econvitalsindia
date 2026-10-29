# Series yaml schema

`scripts/validate_registry.py` enforces this. Required fields:

| Field | Type | Allowed |
|---|---|---|
| id | str | lower_snake, equals the filename, unique |
| title, short_title | str | non-empty |
| area | str | growth, inflation, jobs, activity, money, markets, fiscal, external, states |
| source.agency, source.dataset, source.module | str | module path exists once implemented |
| licence | str | `GODL`, `show-only`, `unverified` (terms not yet read), or `other:<text>` |
| downloadable | bool | must be false when licence is `show-only` or `unverified` |
| fetch | str | auto, manual |
| frequency | str | D, W, F, M, Q, A |
| unit | str | non-empty |
| transforms | list | from 02-conventions.md |
| release.calendar, release.rule, release.lag_days | str/str/int | |
| validation.range | [min, max] | |
| pages | list of {page, section} | page must exist in docs/guidebook/05-pages/ |
| verified_against | list | must be non-empty before a series goes live |
| changes (optional) | str | `none` to show no 1-day/1-week/YTD changes, for balances that can cross zero (e.g. liquidity, flows) |
| step (optional) | bool | true for values that hold until changed (policy rates, reserve ratios): charts draw steps and changes carry the last value forward |
| exclude (optional) | list of {period, reason, added} | published values a person has judged wrong (e.g. an obvious publisher error). They are dropped before publishing and listed on the series page. Never use this to remove inconvenient data; record the evidence in `reason` |
