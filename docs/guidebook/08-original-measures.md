# 08 · Original measures (methods)

Every measure we construct, rather than copy from an agency, is listed here and tagged **Original** on the site. Each entry covers: what it is, why it matters, inputs (series ids), method, limitations, and validation.

## Live

### Core CPI and the "fuel" index
- **What:** CPI excluding food and fuel, using **RBI's definition** so it matches what the MPC looks at. "Fuel" = electricity, gas and other fuels (group 04.5) + fuels and lubricants for personal transport equipment (class 07.2.2: petrol, diesel, CNG). Source of the definition: RBI Bulletin Table 19(c), footnote #, which points to Box IV.2 of the April 2026 Monetary Policy Report.
- **Series:** `cpi_core_index`, `cpi_fuel_index` (`pipelines/sources/derived/core_cpi.py`).
- **Weights** (`registry/weights/cpi2024_core.yaml`): food and beverages 36.75 (MoSPI), core 53.04 (RBI), fuel 10.21 = the remainder. MoSPI does not publish the split of fuel between its two parts in machine-readable form, so `scripts/estimate_core_cpi_weights.py` recovers it. CPI 2024 is fixed-weight, so each parent index is an exact weighted average of its children, and constrained least squares over 21 months gives the shares (max residual 0.007 index points). The estimates are 5.372 + 4.848 = 10.220, scaled to sum to 10.21.
- **Formula:** core = (100·general − 36.75·food − 5.367·elec_gas_fuels − 4.843·vehicle_fuels) / 53.04.
- **Validation (2026-10-28):** vs RBI's published core index for Jun-25, Jul-25, Jun-26 and Jul-26, within 0.01 index points; FY26 average 104.31 = 104.31; y/y Jun-26 3.90 = 3.90, Jul-26 3.87 vs 3.86. Pinned in `tests/sources/test_core_cpi.py`.
- **Limitations:** starts January 2025 (MoSPI's back series exists only for the general index), so y/y starts January 2026. Re-run the weight script if MoSPI revises weights. Weights are fixed until the next base revision.
- **Contributions:** the inflation page shows the percentage-point contributions of food, fuel and core: w·(I_t − I_t−12)/General_t−12. They sum to the published headline rate (checked: Jun–Sep 2026 within 0.01 pp).

### Brent crude in rupees
- **What:** Brent (US$ per barrel, front-month future, Yahoo Finance) × FBIL's USD/INR reference rate. Series `brent_inr` (`pipelines/sources/derived/brent_inr.py`).
- **Method:** each Brent close is converted at the reference rate of the same date, or the latest earlier one within 5 days. Days with no rate that recent are left out, not filled with a stale rate.

### Growth rates "as published" across base years
- **What:** the headline growth series for CPI (`cpi_headline_inflation`), IIP (`iip_general_growth`) and GDP/GVA (`gdp_real_growth`, `gva_*_growth`) show each period's rate **as the agency published it**.
- **Method:** where the new base (CPI 2024, IIP 2022-23, GDP 2022-23) has a rate, it is used. Earlier periods use the old base's published rate. Nothing is recomputed or spliced, and the note column on every row says which base it comes from.
- **Limitations:** rates from two bases differ in basket and weights, so a long chart joins two definitions. Charts say so in their notes.

### Year-on-year changes and other transforms
- **What:** growth rates computed from published index levels (e.g. CPI components, IIP categories, trade) are labelled "computed from the indices" on the site.
- **Method:** % change against the same calendar period a year earlier (matched on the date, not the row position). Because published indices are rounded, a computed rate can differ from the published one by about 0.01–0.1 points. Where an agency publishes the rate itself, we show that and label it "as published".
- **7-day averages** (`7dma`, `7dma_yoy`): for noisy daily series such as electricity demand, a 7-day calendar-window mean (at least 5 observations), and its % change on the same date a year earlier. Moving festivals and weather still distort the year-on-year comparison.

### GST growth on a consistent definition
- **What:** `gst_gross_growth`, `gst_net_growth`.
- **Method:** each month's growth compares that month with the year-earlier column **in the same sheet** of the GST portal's workbook, so both sides use one definition (later sheets exclude the compensation cess). Levels are taken only from each month's own sheet.

## Planned

### Linked series across base years (Phase 2)
- **What:** long series for GDP, CPI and IIP across the 2026 rebasing.
- **Method (default):** ratio splice at the overlap period (back-cast the old series by the ratio of new to old in the overlap year or month). Document the overlap used per series. Do not splice growth rates.
- **Limitations:** composition changes between bases. Show the overlap comparison on the Data & Methods page.

### Seasonally adjusted momentum (Phase 2)
- **What:** 3-month saar for CPI and IIP.
- **Method:** X-13ARIMA-SEATS (statsmodels wrapper) with Indian festival adjustments (Diwali moving holiday) where significant. Parameters stored in the registry.

### Activity and inflation surprise composites (Phase 4)
- **What:** z-scores of each indicator's latest reading vs its own history (rolling 10y), averaged into an activity composite and an inflation composite. India's version of econvitals' "relative to past performance".

### MPC Speak (live)
- **What:** a hawk–dove score for each MPC member's statement in each set of RBI minutes, since October 2016, plus the committee average (`mpc_member_tone`, `mpc_committee_tone`) and each member's vote on the rate resolution (`mpc_member_dissent`, `mpc_dissent_count`).
- **Method:** each statement is split out of the minutes by matching the "Statement by" headings to the names in the vote table. We count phrases from a fixed lexicon (`registry/mpc/lexicon.yaml`, version 1; regular expressions, case-insensitive, whole words). Score = (hawkish − dovish) / (hawkish + dovish + 2), so above zero leans hawkish and below zero leans dovish. The +2 keeps a statement with one or two hits near zero. No language model is used. That replaces the earlier plan for an LLM-scored rubric, for cost and so that anyone can reproduce a score from the text.
- **How it was built:** lexicon v1 was written before any scores were seen. The +2 shrinkage was added after looking at the hit counts of one meeting (August 2026, one to five phrases per statement), before the full history was scored.
- **Checks (28 Oct 2026, 62 meetings, using only the minutes themselves):** the decision comes from each rate resolution's wording ("to reduce / keep / increase").
  - **Committee average by decision:** −0.55 at the 13 meetings that cut, −0.10 at the 40 holds and +0.39 at the 9 hikes.
  - **Correlation with decisions:** 0.72 with the direction decided at the same meeting and 0.58 with the next meeting's.
  - **Dissenters:** among dissents whose statement says they wanted a cut (6 cases, by a simple "I vote to reduce/cut" match), the dissenter scored on average 0.30 below the median of the other members.
  - **Caveat on the checks:** a statement is written to justify the vote, so these checks show the score reads statements sensibly, not that it predicts anything.
- **Limits:** no negation handling ("no longer see upside risks to inflation" counts as hawkish). Members differ in length and style, so compare a member with themselves over time rather than members with each other. The vote table does not record which way a dissenter wanted the rate to move.
- **Changing the lexicon:** edit the yaml, bump `version`, add a changelog line, then run `MPC_RESCAN=1 make update SOURCE=rbi_mpc_minutes` (about 3 minutes) and `make update SOURCE=derived_mpc_committee`. Every changed score is logged in `data/revisions/`. Rerun the checks above and update them here.

### RBI policy rule (Phase 4)
- To be specified.
