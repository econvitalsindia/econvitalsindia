# Playbook: scout a data source

**Output:** an updated row in `docs/guidebook/03-data-sources.md` with status `scouted`.

Find and record:
1. **Exact URL pattern** for the latest release and for history (does it change monthly? is there an archive page?).
2. **Format:** API (JSON/CSV/SDMX), Excel, PDF (text or scanned?), or HTML table.
3. **Release timing:** day and time pattern, plus any official calendar URL.
4. **Access:** fetch with `curl -A "Mozilla/5.0"` from your machine. Does it need cookies or JS? (Testing from a US IP, e.g. a GitHub Actions `workflow_dispatch` of `scripts/probe_url.py`, decides `auto` vs `manual`.)
5. **Licence or terms:** GODL statement, copyright notice, or terms page. Quote the relevant line.
6. **History depth and revisions:** how far back, and whether past values get revised.
7. **Quirks:** units, base year, footnotes, and seasonally adjusted vs not.

Don't write a parser in this step. Record the findings and stop.
