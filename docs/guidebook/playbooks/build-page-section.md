# Playbook: build a page section

**Input:** a page and a section from `docs/guidebook/05-pages/<page>.md`. **Output:** a PR with the section live in the local build.

1. Read the page checklist in full, including **Must NOT include**.
2. Confirm every series the section needs exists in `registry/series/`. If not, run `add-indicator.md` first (as a separate PR).
3. Add or update the section in `registry/pages/<page>.yaml` (sections → series → chart type → transforms).
4. Build the component in `site/src/components/` using the existing chart and table components. Read the site name and colours from config, never literals.
5. Follow `02-conventions.md` (units, labels, footers, reference lines, download/cite buttons).
6. `make build && make dev`. Check at desktop and at 375 px width.
7. Run `qa-site.md` for that page.
8. Tick the checklist items in `05-pages/<page>.md`, with the PR number.
