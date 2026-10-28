# Page specs (machine-readable)

One yaml per page, mirroring `docs/guidebook/05-pages/<page>.md`:

```yaml
page: inflation
title_key: inflation          # i18n key, not a literal string
sections:
  - id: summary-table
    kind: table               # table | line | bar | stacked | curve | map | tiles
    series: [cpi_headline_index, cpi_food_index]
    transforms: [yoy]
```
Populated from Phase 1.
