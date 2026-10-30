# Money & banking

**Purpose:** What is the RBI's policy stance, how tight is liquidity, and how fast are credit and deposits growing?

## Must include
- [x] Policy corridor chart: repo, SDF, MSF, with WACR overlaid (weekly from WSS; daily snapshots since 28 Oct 2026)
- [x] Table of MPC decisions: date, decision, vote split, stance wording (from the resolution in the minutes; `mpc_repo_decision`, built into `mpc_decisions.json`). Size splits ("1 member voted for 25 bp") are shown where the minutes record them
- [x] Next MPC date and countdown (from `registry/calendar/rbi.yaml`; the countdown is fixed at build time)
- [x] Net liquidity (₹ lakh crore, + = surplus), daily, from WSS table 8 (`liquidity_surplus`; RBI's sign flipped). It covers all RBI operations, not LAF alone
- [x] CRR and SLR with change dates
- [x] Scheduled commercial bank credit and deposit growth y/y (fortnightly), plus the credit–deposit ratio (site calculation)
- [x] Sectoral deployment of credit (monthly): industry, services, personal loans, agriculture (`rbi/sectoral_credit.py`, growth as published)
- [x] Money supply M3 growth, reserve money (WSS tables 6 and 7, fortnightly)
- [x] T-bill yields (91d, 182d, 364d) (CP and CD rates: parser in rbi/wss.py tables 10–11, waiting on first successful download)

## Must NOT include
- Fed-style "market-implied path" unless we have a free, redistributable OIS source (we probably don't; leave it out)
- Bank-level data (out of scope)

## Series (planned)
repo_rate, sdf_rate, msf_rate, wacr, liquidity_surplus, mpc_repo_decision, crr, slr, scb_credit, scb_deposits, credit_<sector>, m3, m3_growth, currency_public_growth, reserve_money, reserve_money_growth, tbill_91d, tbill_182d, tbill_364d

## Phase
1 (repo, WACR, credit), 2 (page)
