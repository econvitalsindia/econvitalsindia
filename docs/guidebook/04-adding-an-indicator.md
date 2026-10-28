# 04 · Adding an indicator

The recipe agents follow is `playbooks/add-indicator.md`. This page is the human-readable version, with the reasons behind each step.

## Steps

1. **Check it isn't already there.** Search `registry/series/` and `registry/backlog.yaml`.
2. **Scout the source** if `03-data-sources.md` doesn't mark it `scouted`. See `playbooks/scout-source.md`.
3. **Pick a series id**: `<area>_<concept>[_<detail>]`, lower snake case, stable forever. Examples: `cpi_headline_index`, `cpi_food_index`, `gdp_real_level`, `gsec_10y_yield`, `upi_volume`. Transforms are **not** part of the id; they are computed. Linked series get the suffix `_linked`.
4. **Write `registry/series/<id>.yaml`** from `_template.yaml`. Every field matters:
   - `licence` and `downloadable` decide whether the CSV button appears.
   - `fetch: auto|manual` decides which job runs it.
   - `release` decides when the healthcheck calls it overdue.
   - `range` and `revision_alert` drive validation.
   - `pages` decides where it appears.
5. **Write the source module** `pipelines/sources/<agency>/<dataset>.py`, subclassing `pipelines.core.Source`. One module can produce several series (one CPI file → headline, food, fuel…).
6. **Save a raw fixture** to `tests/fixtures/<agency>/<dataset>/<date>.<ext>`. Keep it small and trim it if it's huge. Write a parser test that pins three or more known values from the official release.
7. **Run** `make update SOURCE=<id>` and inspect `data/series/<id>.csv`.
8. **Verify against the official release.** Compare the latest two values, plus one value from 2+ years ago, against the agency's PDF or press release. Record the check in the yaml under `verified_against` (url, date, by whom).
9. **Wire it to a page.** Add it to `registry/pages/<page>.yaml` and tick the matching line in `docs/guidebook/05-pages/<page>.md`.
10. **Remove it from `registry/backlog.yaml`** if it was listed there.
11. **Open a PR** using the template. `make check` must pass.

## Definition of done

- [ ] yaml complete, with `verified_against` filled in
- [ ] parser test with a fixture
- [ ] `make update SOURCE=<id>` works from a clean checkout (and from Actions if `fetch: auto`)
- [ ] appears on its page with correct units, base year and source footer
- [ ] Data & Methods page lists it (automatic from the registry; check it rendered)
- [ ] if constructed by us (core CPI, linked series, seasonal adjustment): method written in `08-original-measures.md`
