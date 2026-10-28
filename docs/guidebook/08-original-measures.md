# 08 · Original measures (methods)

Every measure we construct, rather than copy from an agency, is listed here and tagged **Original** on the site. Each entry covers: what it is, why it matters, inputs (series ids), method, limitations, and validation.

## Planned

### Core CPI and the "fuel" index (Phase 1, **live**)
- **What:** CPI excluding food and fuel, using **RBI's definition** so it matches what the MPC looks at. "Fuel" = electricity, gas and other fuels (group 04.5) + fuels and lubricants for personal transport equipment (class 07.2.2: petrol, diesel, CNG). Source of the definition: RBI Bulletin Table 19(c), footnote #, which points to Box IV.2 of the April 2026 Monetary Policy Report.
- **Series:** `cpi_core_index`, `cpi_fuel_index` (`pipelines/sources/derived/core_cpi.py`).
- **Weights** (`registry/weights/cpi2024_core.yaml`): food and beverages 36.75 (MoSPI), core 53.04 (RBI), fuel 10.21 = the remainder. MoSPI does not publish the split of fuel between its two parts in machine-readable form, so `scripts/estimate_core_cpi_weights.py` recovers it. CPI 2024 is fixed-weight, so each parent index is an exact weighted average of its children, and constrained least squares over 21 months gives the shares (max residual 0.007 index points). The estimates are 5.372 + 4.848 = 10.220, scaled to sum to 10.21.
- **Formula:** core = (100·general − 36.75·food − 5.367·elec_gas_fuels − 4.843·vehicle_fuels) / 53.04.
- **Validation (2026-10-28):** vs RBI's published core index for Jun-25, Jul-25, Jun-26 and Jul-26, within 0.01 index points; FY26 average 104.31 = 104.31; y/y Jun-26 3.90 = 3.90, Jul-26 3.87 vs 3.86. Pinned in `tests/sources/test_core_cpi.py`.
- **Limitations:** starts January 2025 (MoSPI's back series exists only for the general index), so y/y starts January 2026. Re-run the weight script if MoSPI revises weights. Weights are fixed until the next base revision.
- **Contributions:** the inflation page shows the percentage-point contributions of food, fuel and core: w·(I_t − I_t−12)/General_t−12. They sum to the published headline rate (checked: Jun–Sep 2026 within 0.01 pp).

### Linked series across base years (Phase 2)
- **What:** long series for GDP, CPI and IIP across the 2026 rebasing.
- **Method (default):** ratio splice at the overlap period (back-cast the old series by the ratio of new to old in the overlap year or month). Document the overlap used per series. Do not splice growth rates.
- **Limitations:** composition changes between bases. Show the overlap comparison on the Data & Methods page.

### Seasonally adjusted momentum (Phase 2)
- **What:** 3-month saar for CPI and IIP.
- **Method:** X-13ARIMA-SEATS (statsmodels wrapper) with Indian festival adjustments (Diwali moving holiday) where significant. Parameters stored in the registry.

### Activity and inflation surprise composites (Phase 4)
- **What:** z-scores of each indicator's latest reading vs its own history (rolling 10y), averaged into an activity composite and an inflation composite. India's version of econvitals' "relative to past performance".

### MPC Speak (Phase 4)
- **What:** an LLM-scored hawk–dove score for each MPC member's statement in each set of minutes.
- **Method:** published rubric and prompt, temperature 0, two models scoring for agreement, and a human check on a 10% sample. The score is shown next to the text.

### RBI policy rule (Phase 4)
- To be specified.
