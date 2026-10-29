# Tools (index)

**Purpose:** Deeper interactive tools on narrower questions.

## Planned tools (Phase 4+), in priority order
- [x] **MPC Speak** (/money/mpc-speak/): hawk–dove score for each MPC member's statement in every set of minutes since October 2016, from a published phrase lexicon (no LLM; decided 2026-10-28 for cost and reproducibility). Shows the committee average over time, the latest meeting member by member with phrase counts and votes, and the last eight meetings. Method and validation: 08-original-measures.md
- [ ] **Surprise composites**: activity and inflation z-scores vs history (and vs consensus, if a free consensus source appears)
- [x] (Growth-gap version, `/tools/policy-rule/`; output gap once a linked GDP series exists) **RBI policy rule**: Taylor-type rule with user-chosen neutral rate, inflation gap (headline/core), output gap (HP/production function), vs actual repo
- [x] (`/tools/budget/`, Expenditure Profile Statement 3, demand-level totals; major heads not yet) **Union Budget explorer**: BE/RE/Actuals by ministry and major heads, over time
- [ ] **Monsoon and food watch**: rainfall vs LPA by subdivision, reservoir storage, daily prices of key vegetables, vs CPI food
- [ ] **Base-year bridge explorer**: old vs new base series in the overlap period
- [x] (`/tools/peers/`: BIS policy rates and CPI, World Bank GDP; IMF API returns 403) **India vs peers**: growth, inflation and policy rates vs EM peers (IMF/World Bank data)

## Must NOT include
- Tools that need a server at runtime (everything precomputed or client-side)
