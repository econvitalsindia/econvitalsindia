# Fiscal

**Purpose:** Is the Union government on track for its budgeted deficit, and how are revenues and capex doing?

## Must include
- [x] Fiscal deficit FYTD as % of Budget Estimate, vs the same point in the previous 3 years
- [ ] Revenue: gross tax revenue, net tax to Centre, non-tax, disinvestment, FYTD vs BE
- [x] Spending: revenue expenditure, capital expenditure, interest payments, FYTD vs BE
- [x] GST gross collections (monthly, y/y)
- [x] Tax collections by head (CGA DTL3, from FY 2015-16): gross, direct (corporate + income), STT, customs, excise
- [x] Union Budget headline numbers (BE, RE, Actuals) for the current and last FY (panels `budget_be`, `budget_re`, `budget_actuals` from Budget at a Glance; table built into `budget.json`)
- [ ] General government (Centre + states) deficit and debt, % of GDP (annual)
- [ ] States: link to the States page for state fiscal ratios

## Must NOT include
- Deficit % of GDP for a partial year without stating the GDP used
- Mixing BE and RE without labelling

## Series (planned)
cga_fiscal_deficit_fytd, cga_gross_tax_fytd, cga_direct_tax_fytd, cga_corporate_tax_fytd, cga_income_tax_fytd, cga_capex_fytd, cga_revex_fytd, cga_interest_fytd, budget_fd_be, gst_gross_collections, gg_deficit_pct_gdp, gg_debt_pct_gdp

## Phase
1 (fiscal deficit, GST), 2 (page), 4 (Budget explorer tool)
