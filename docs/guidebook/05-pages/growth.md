# Growth (GDP and national accounts)

**Purpose:** How fast is the economy growing, which sectors and demand components drive it, and how does it compare with RBI's projections?

## Must include
- [x] Table: real GDP and GVA growth, latest quarter and four-quarter average, by expenditure (PFCE, GFCE, GFCF, exports, imports) and by sector (agriculture, industry, manufacturing, construction, services subsectors)
- [x] Chart: real GDP growth y/y, quarterly, 5 years, with RBI projection for the current FY marked
- [x] Chart: contributions to real GDP growth by expenditure component (stacked bars)
- [x] Chart: nominal vs real GDP growth and the implicit deflator
- [ ] Annual estimates: First Advance / Second Advance / Provisional / Revised for the latest FYs, showing how estimates were revised
- [x] Discrepancies line shown explicitly (as the residual 'Other' bar, with its size in the note)
- [ ] Base year label (2022-23) and a note on the 2026 rebasing, linking to the base-year bridge
- [ ] Detail page `/growth/detail`: full sector-by-sector tables, nominal levels in ₹ lakh crore

## Must NOT include
- Old-base (2011-12) and new-base (2022-23) growth on one line without the linked series
- q/q annualised growth as the headline (MoSPI doesn't publish SA data; any SA q/q is an Original and labelled)
- Private nowcasts we can't attribute or redistribute

## Series (planned)
gdp_real_level, gdp_nominal_level, gva_real_level, gva_real_<sector>, gdp_real_<component>, gdp_deflator, rbi_gdp_projection

## Done when
Table matches the MoSPI press release for the latest quarter to 1 decimal. Contributions sum to GDP growth within the discrepancy.

## Phase
1 (headline series), 2 (page)
