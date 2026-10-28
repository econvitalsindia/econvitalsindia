# Briefing templates

One markdown file per release note. Front matter: `name`, `title`, `trigger` (the series
whose new observation triggers a draft), `views` (series ids, optionally `id:transform`).
The body may contain **no digits**: every number is a token such as
`{{cpi_headline_inflation.latest}}`, `{{cpi_core_index:yoy.change_phrase}}` or
`{{const.rbi_inflation_target}}`. Facts are listed in `pipelines/briefings/ledger.py`.
`make check` fails a template with a typed number or an unknown token.
Write sentences that stay true whichever way the numbers move (use `change_phrase`).
