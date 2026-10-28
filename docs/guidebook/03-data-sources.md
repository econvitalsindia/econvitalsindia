# 03 · Data sources catalogue

One row per **publisher/dataset**. Each indicator built from a source also has a `registry/series/*.yaml` that points back here.

**Status key:** `to-scout` = not yet checked · `scouted` = format, URL pattern, licence and access checked (date in Notes) · `live` = a series is in production.
**Access:** `auto` = works from GitHub Actions (US IP) · `manual` = needs a machine in India · `?` = untested.
**Licence:** `GODL` = Government Open Data Licence – India (redistribute with attribution) · `show-only` = display with attribution, no bulk download · `check` = unknown.

Every entry below is **`to-scout`**. The URLs are portal home pages, not verified endpoints. The Phase 0/1 source-scout pass fills in Format, URL pattern and Notes. Use `playbooks/scout-source.md`.

## Official statistics

| Publisher | Datasets | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|---|
| MoSPI (NSO) | National accounts (quarterly GDP/GVA, AE/PE), CPI (base 2024), IIP (base 2022-23), PLFS (monthly, quarterly, annual) | mospi.gov.in; eSankhyiki: esankhyiki.mospi.gov.in | ? | GODL | to-scout | eSankhyiki has an API and a pilot MCP server. Check endpoints, auth and rate limits. Release calendar (ARC) is a PDF on mospi.gov.in |
| Office of the Economic Adviser (DPIIT) | WPI, Index of Eight Core Industries | eaindustry.nic.in | ? | GODL | to-scout | Monthly, around the 14th (WPI) and 20th (core) |
| Labour Bureau | CPI-IW, CPI-AL/RL | labourbureau.gov.in | ? | GODL | to-scout | |
| EPFO | Net payroll additions | epfindia.gov.in | ? | GODL | to-scout | Monthly, heavily revised. Store vintages |
| MGNREGA (MoRD) | Households demanding work, person-days | nrega.nic.in | ? | GODL | to-scout | Report pages are slow and stateful |

## RBI

| Dataset | Portal | Access | Licence | Status | Notes |
|---|---|---|---|---|---|
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
| Grid-India | Daily all-India peak demand, energy met | grid-india.in | ? | check | to-scout | Daily PSP report (PDF/Excel) |
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
| Central Water Commission | Reservoir storage bulletin (weekly) | cwc.gov.in | ? | GODL | to-scout | PDF |
| Dept of Consumer Affairs | Daily retail prices of essential commodities (tomato, onion, potato, pulses) | fcainfoweb.nic.in | ? | GODL | to-scout | |

## International comparisons (Phase 4)

| Publisher | Datasets | Access | Licence | Status |
|---|---|---|---|---|
| IMF (WEO, IFS via SDMX), World Bank WDI API | Peer comparisons | auto | open with attribution | to-scout |

## Never use

CMIE (paywalled), Bloomberg/Refinitiv/LSEG terminal data, any data behind a login, any source whose terms forbid redistribution.
