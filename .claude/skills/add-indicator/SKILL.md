---
name: add-indicator
description: Add a new economic indicator (series) to the site end-to-end. Use when asked to add, onboard or build a series/indicator, or when picking up a registry/backlog.yaml item.
---
Follow `docs/guidebook/playbooks/add-indicator.md` step by step. Background and the definition of done: `docs/guidebook/04-adding-an-indicator.md`. Conventions: `docs/guidebook/02-conventions.md`.

Hard rules from `AGENTS.md` apply: no hard-coded site name, pinned test values come from the official release (not our output), never hand-edit `data/series/*.csv`.

For the source check, delegate to the `source-scout` subagent if `03-data-sources.md` shows the source as `to-scout`. For the final check, delegate to the `data-validator` subagent.
