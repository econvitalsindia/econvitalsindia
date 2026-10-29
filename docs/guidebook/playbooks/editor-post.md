# Playbook: a "From the editor" post

Human-written posts sit in the Briefings list with a "From the editor" badge. They are not drafted from the ledger, so the number checker does not apply; quote figures from the site's data pages (or cite another source) and keep to the editorial policy's tone rules.

1. Create `site/src/content/briefings/<YYYY-MM-DD>-<short-slug>.md`:

   ```markdown
   ---
   title: "Why the food inflation numbers matter this winter"
   date: 2026-11-05
   product: editor
   author: Bishmay Barik
   ---
   The post, in Markdown. Link to pages such as [Inflation](/inflation/#food-watch).
   ```

2. `make build` and read it at `/briefings/<slug>/`.
3. Open a pull request (or push, if you are the maintainer). Corrections later: add `corrections:` to the front matter (07-editorial-policy.md).
