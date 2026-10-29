# Home dashboard

**Purpose:** In 60 seconds, how is the Indian economy doing, and what's coming up?

## Must include
- [x] "As of" date in the header (latest data date across series, IST)
- [x] Key-indicator strip (19 tiles as of 2026-10-29). Each shows value, period and change, and links to its page:
  - [x] Real GDP growth (% y/y, latest quarter)
  - [x] CPI headline (% y/y)
  - [x] Core CPI (% y/y, Original, RBI definition)
  - [x] IIP (% y/y)
  - [x] Unemployment rate (PLFS monthly, CWS, 15+)
  - [x] Repo rate (with date of last change)
  - [x] 10-year G-sec yield (bp change YTD)
  - [x] Nifty 50 and Sensex (% YTD)
  - [x] USD/INR (FBIL reference, % YTD)
  - [x] Brent in ₹ per barrel (% YTD)
  - [x] FX reserves (US$ bn, weekly)
  - [x] GST collections (% y/y)
- [x] "India in four questions" cards (external uses trade balance and reserves; CAD to add), each with 2–3 numbers and a link:
  1. Is inflation near 4%? (CPI y/y, core y/y, 3-month momentum, the 2–6% band)
  2. Is growth holding up? (real GDP y/y, GVA y/y, private consumption y/y)
  3. Are jobs being created? (PLFS unemployment and LFPR now vs a year ago, EPFO net adds 3mma)
  4. Is the external position under strain? (CAD % GDP, reserves in months of imports, INR YTD)
- [x] "Today / coming up" strip from the calendar (next 5 releases)
- [ ] Newsletter signup (hidden until Phase 3; behind `newsletter.enabled`)
- [x] One summary table per topic (as econvitals does), each linking to its page
- [x] Footer credit line from `site.config.yaml → credit.inspired_by_text`

## Must NOT include
- Any number not generated from `data/series`
- Market data older than 1 trading day without a visible "stale" badge
- More than 12 tiles in the strip (move extras to topic pages)
- Opinions or forecasts of our own on the home page (Originals are allowed, tagged)

## Series
gdp_real_level, cpi_headline_index, cpi_core_index (Original), iip_general_index, plfs_ur_monthly, repo_rate, gsec_10y_yield, nifty50_close, sensex_close, usdinr_fbil, brent_usd + usdinr (→ Brent in ₹), fx_reserves_total, gst_gross_collections

## Done when
All tiles render from data. Every tile links to the right page. Values match the official latest release (spot check 5). Mobile layout has no horizontal scroll.

## Phase
1 (strip + four questions + calendar strip); 2 (topic summary tables)
