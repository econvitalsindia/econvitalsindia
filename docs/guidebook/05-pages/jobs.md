# Jobs

**Purpose:** Is employment growing, and how do urban, rural, female and youth labour markets look?

## Must include
- [x] PLFS monthly (CWS, 15+): unemployment rate, LFPR, WPR, for all/rural/urban and male/female
- [x] Youth (15–29) unemployment
- [x] PLFS quarterly bulletin (urban) and annual (usual status), with a clear concept label (CWS vs usual status)
- [x] EPFO net payroll additions, with a note that it measures formalisation, not total jobs, and is heavily revised (`epfo_net_payroll`, manual; monthly level shown, not 3mma, because the series stopped at Jul 2025)
- [ ] MGNREGA households demanding work vs a year ago (rural distress signal). Scouted 2026-10-29: nrega.nic.in redirects to nrega.dord.gov.in; national reports at mnregaweb4.dord.gov.in/netnregarep/MISreport4.aspx are ASP.NET forms needing postbacks, and nreganarep.nic.in timed out
- [x] Chart: female LFPR over time (long annual series, usual status, from 2017-18)
- [x] Concept box: CWS vs usual status (ps+ss), and why they differ

## Must NOT include
- Mixing CWS and usual-status figures on one line
- CMIE unemployment (paywalled)
- EPFO presented as "jobs created" without the caveat

## Series (planned)
plfs_ur_monthly, plfs_lfpr_monthly, plfs_wpr_monthly (+ rural/urban/male/female/youth variants), plfs_ur_annual_ps_ss, epfo_net_payroll, mgnrega_hh_demanded

## Done when
Monthly PLFS values match the bulletin for the last 3 months. Concept labels are on every chart.

## Phase
1 (PLFS monthly headline), 2 (page)
