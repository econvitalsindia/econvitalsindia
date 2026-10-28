# 09 · Rebranding (changing the site name or domain)

The name is defined **only** in `site.config.yaml`.

## Rename

1. Edit `site.name`, `site.short_name`, `site.tagline` in `site.config.yaml`.
2. Replace `assets/brand/` wordmark files if they contain text (the mark itself is name-independent).
3. `make check` (the name check now looks for the *new* name outside config, so it catches nothing old). Also run `scripts/check_name.py --also "<old name>"` to catch leftovers.
4. Rebuild and deploy.
5. Optional: rename the GitHub repo or org. GitHub keeps redirects.

## New domain

1. Add the domain in Cloudflare Pages → Custom domains.
2. Set `site.url` in `site.config.yaml` (used for canonical URLs, RSS, sitemaps, OG tags).
3. Update the newsletter provider's sender domain (SPF/DKIM) if emailing from the domain.
