# 03 · Data sources catalogue

One row per **publisher/dataset**. Each indicator built from a source also has a `registry/series/*.yaml` that points back here.

**Status key:** `to-scout` = not yet checked · `scouted` = format, URL pattern, licence and access checked (date in Notes) · `live` = a series is in production.
**Access:** `auto` = works from GitHub Actions (US IP) · `manual` = needs a machine in India · `?` = untested.
**Licence:** `GODL` = Government Open Data Licence – India (redistribute with attribution) · `show-only` = display with attribution, no bulk download · `check` = unknown.

Every entry below is **`to-scout`**. The URLs are portal home pages, not verified endpoints. The Phase 0/1 source-scout pass fills in Format, URL pattern and Notes. Use `playbooks/scout-source.md`.

## Reachability probe: 2026-10-28

`scripts/probe_sources.py` fetched each portal's home page with browser headers, from India (this Mac) and from GitHub Actions (US). Raw results: `data/probes/*.json`. Re-run with the `probe-sources` workflow. **Home pages only**: a data endpoint can behave differently, so confirm per endpoint when scouting.

| Portal | India | Actions (US) | Implication |
|---|---|---|---|
| MoSPI, eSankhyiki, Labour Bureau, NREGA, RBI (all three), CGA, PIB, indiabudget, Commerce, TradeStat, FBIL, CCIL, BSE, NSDL, AMFI, PPAC, DGCA, IMD, FCA prices, GST, World Bank API | 200 | 200 | `auto` candidates |
| EPFO | 200 | **403** | `manual` |
| Grid-India | 200 | **connection reset** | `manual` |
| CWC (reservoirs) | 200 | **401** | `manual` |
| NSE home page | 403 | 403 | Home page blocks scripts, but `nseindia.com/api/allIndices` returned 200 from both. Licensed: show-only |
| NPCI | 403 | 403 | Blocks scripts everywhere. Try a browser-like session or the PDF statistics pages; else manual entry |
| Yahoo chart API | 429 | 429 | Rate-limited without a session. Use the `yfinance` library (handles cookies) and test it |
| OEA / DPIIT (WPI, core) | SSL error | SSL error | The server sends an incomplete certificate chain. Fix: supply the intermediate certificate to httpx (don't disable verification) |

Small 200 responses (MoSPI 2.6 KB, eSankhyiki 1.2 KB, NREGA 0.5 KB, FBIL 1.5 KB) are JavaScript shells or redirects. Their data must come from API or file endpoints, not from parsing HTML.

## Official statistics

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| MoSPI (NSO) | CPI (base 2024 + official back series to 2013), IIP, NAS (GDP, base 2022-23), PLFS, WPI | REST API `https://api.mospi.gov.in/api/<product>/...` (no key). Specs: `https://esankhyiki.mospi.gov.in/layout/swagger_user_<cpi|iip|nas|plfs|wpi>.yaml`. Codes: MCP server `https://mcp.mospi.gov.in/mcp` tool `get_metadata` | auto | GODL (released under NDSAP/GSDD) | **live**: CPI, IIP, NAS quarterly, PLFS monthly | Scouted 2026-10-28. Needs TLS legacy renegotiation (handled in `core/http.py`). Max 100 rows/page (base 2012) or 200 (base 2024). CPI 2024 base uses COICOP 2018 divisions (no 'fuel and light' group). Back series covers the general index only. IIP: `iip/getIIPData` frequency=Monthly, base 2022-23 from Apr 2023, 2011-12 before; types General / Sectoral / Use-based category. NAS: `nas/getNASData` (indicators 5 GDP, 9-15 components, 21 GVA growth, 22 GDP growth; the old-base total row is called 'Total GVA Growth Rate'). PLFS: `plfs/getData` frequency_code=3 monthly from 2025, one indicator per call. CPI params: base_year, series (Current/Back), state_code (1 = All India for 2024; 99 for 2012), sector_code (1 R, 2 U, 3 C), division_code; 2012 base needs level=Group |
| Office of the Economic Adviser (DPIIT) | WPI, Index of Eight Core Industries | eaindustry.nic.in | ? | GODL | to-scout | Monthly, around the 14th (WPI) and 20th (core). **The MoSPI API's WPI (`/api/wpi/getWpiRecords`) stops at April 2026 on the 2011-12 base (checked 2026-10-28), so WPI must come from OEA.** OEA's server sends an incomplete certificate chain |
| Labour Bureau | CPI-IW, CPI-AL/RL | labourbureau.gov.in | ? | GODL | to-scout | |
| EPFO | Net payroll additions | epfindia.gov.in | manual | GODL | to-scout | Monthly, heavily revised. Store vintages |
| MGNREGA (MoRD) | Households demanding work, person-days | nrega.nic.in | ? | GODL | to-scout | Report pages are slow and stateful |

## RBI

| Dataset | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|
| RBI home page rates panel: repo/SDF/MSF, CRR/SLR, FBIL rates (1 pm today), benchmark G-sec yields, T-bill cut-offs, Sensex/Nifty closes | www.rbi.org.in | auto | unverified | **live** | Scouted 2026-10-28. Snapshot only (no history): we store one value per day. Footnotes give the 'as on' dates |
| DBIE time series (money, credit, rates, BoP, reserves, state finances) | data.rbi.org.in (moved from dbie.rbi.org.in, June 2024) | ? | check (RBI terms) | to-scout | No documented public API found. Scrape downloads |
| Weekly Statistical Supplement (WSS) | rbi.org.in | ? | check | to-scout | Friday. FX reserves, liquidity, rates |
| Press releases: MPC statements, minutes, policy rates | rbi.org.in | ? | check | to-scout | Minutes carry each member's statement (MPC Speak, Phase 4) |
| Household Inflation Expectations Survey, Consumer Confidence | rbi.org.in | ? | check | to-scout | Bi-monthly, with the MPC cycle |
| Monetary Policy Report projections | rbi.org.in | ? | check | to-scout | Twice a year + each policy statement |

## Government finance

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| Controller General of Accounts | Centre's monthly accounts | cga.nic.in | ? | GODL | to-scout | Last working day of month, with a 1-month lag |
| Ministry of Finance / PIB | GST collections, direct tax collections | pib.gov.in, gst.gov.in | ? | GODL | to-scout | GST on the 1st of the month via press release |
| Union Budget | BE/RE/Actuals | indiabudget.gov.in | ? | GODL | to-scout | Budget Explorer (Phase 4) |
| PRS Legislative Research | State budget analyses | prsindia.org | ? | check | to-scout | Secondary. Prefer RBI State Finances |

## External sector

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| Ministry of Commerce | Monthly merchandise + services trade (press release), TradeStat | commerce.gov.in, tradestat.commerce.gov.in | ? | GODL | to-scout | Mid-month |
| RBI | BoP/CAD (quarterly), FX reserves (weekly), REER/NEER, ECB, remittances | data.rbi.org.in | ? | check | to-scout | |

## Markets and finance

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| FBIL | Reference rates (USD/INR etc.), G-sec valuation, T-bill curves | fbil.org.in | ? | check | to-scout | Official benchmark for INR |
| CCIL | G-sec yields, money-market volumes | ccilindia.com | ? | check | to-scout | Often blocks foreign IPs (likely `manual`) |
| NSE / BSE | Index levels, India VIX, FII/DII provisional flows | nseindia.com, bseindia.com | ? (NSE blocks non-browser clients) | **show-only** | to-scout | Licensed. No bulk downloads |
| Yahoo Finance (via yfinance) | ^NSEI, ^BSESN, INR=X, Brent, gold | — | auto (likely) | **show-only** | to-scout | Convenience source for levels. Cross-check against NSE/FBIL |
| NSDL | FPI flows (equity, debt) | fpi.nsdl.co.in | ? | check | to-scout | |
| AMFI | Mutual fund flows, SIP inflows, AUM | amfiindia.com | ? | check | to-scout | Monthly, ~10th |
| SEBI | Bulletin aggregates | sebi.gov.in | ? | check | to-scout | Later |

## High-frequency activity

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| Grid-India | Daily all-India peak demand, energy met | grid-india.in | manual | check | to-scout | Daily PSP report (PDF/Excel) |
| NPCI | UPI volumes and values (monthly; daily from product statistics) | npci.org.in | ? | check | to-scout | |
| PPAC | Petroleum product consumption | ppac.gov.in | ? | GODL | to-scout | |
| DGCA | Domestic air passengers | dgca.gov.in | ? | GODL | to-scout | Monthly PDF |
| SIAM / FADA | Vehicle wholesales / retail registrations | siam.in, fada.in | ? | check | to-scout | Industry bodies. Check terms. Vahan dashboard as an alternative |
| GSTN | E-way bills | gst.gov.in / ewaybillgst.gov.in | ? | GODL | to-scout | |
| Indian Railways | Freight loading | pib.gov.in | ? | GODL | to-scout | Via press releases |
| S&P Global | HSBC India PMI (headline) | — | — | **show-only, cite headline only** | to-scout | Licensed. Never redistribute series |

## Monsoon, agriculture, food

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| IMD | Rainfall vs long-period average (weekly, seasonal) | mausam.imd.gov.in | ? | check | to-scout | June–September focus |
| Central Water Commission | Reservoir storage bulletin (weekly) | cwc.gov.in | manual | GODL | to-scout | PDF |
| Dept of Consumer Affairs | Daily retail prices of essential commodities (tomato, onion, potato, pulses) | fcainfoweb.nic.in | ? | GODL | to-scout | |

## International comparisons (Phase 4)

| Publisher | Datasets | Access | Licence | Status |
|---|---|---|---|---|
| IMF (WEO, IFS via SDMX), World Bank WDI API | Peer comparisons | auto | open with attribution | to-scout |

## Never use

CMIE (paywalled), Bloomberg/Refinitiv/LSEG terminal data, any data behind a login, any source whose terms forbid redistribution.
