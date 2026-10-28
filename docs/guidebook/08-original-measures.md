# 08 · Original measures (methods)

Every measure we construct, rather than copy from an agency, is listed here and tagged **Original** on the site. Each entry covers: what it is, why it matters, inputs (series ids), method, limitations, and validation.

## Planned

### Core CPI (Phase 1)
- **What:** CPI excluding food and energy.
- **Open question (2026-10-28):** the 2024 base uses COICOP 2018 divisions, so there is no "fuel and light" group any more. Energy now sits inside division 04 (housing, water, electricity, gas and other fuels) and division 07 (transport: fuels and lubricants). Core therefore has to be built from class or item indices with 2024 weights. Agree the exact exclusion list with the maintainer before building it.
- **Method:** re-weight the remaining classes using the 2024-base weights. The index is the weighted average of group indices, normalised. Also publish the variant that additionally excludes petrol, diesel (vehicle fuel) and gold, if item indices are available.
- **Validate:** compare with published third-party core estimates for the last 12 months. Must be within 0.1 pp. Record the result here.

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
