# Markets

**Purpose:** Where are Indian rates, equities, the rupee and commodities, and what moved today?

## Must include
- [ ] Cross-asset table (as econvitals does): Latest, 1-day, 1-week, YTD for:
  - Rates: 91d T-bill, 2y, 5y, 10y, 30y G-sec, 2s10s slope (bp)
  - Equities: Nifty 50, Sensex, Nifty Bank, Nifty IT, Nifty Midcap 100, India VIX
  - FX: USD/INR (FBIL), EUR/INR, JPY/INR, GBP/INR, CNY/INR
  - Commodities: Brent ($ and ₹), gold (₹/10g), silver
- [ ] "Markets updated" timestamp (IST)
- [ ] G-sec yield curve: latest vs 1 month ago vs end of last FY
- [ ] Chart: 10y G-sec vs repo rate (term spread)
- [ ] Chart: Nifty 50 with P/E (if a redistributable source exists; otherwise omit)
- [ ] FPI flows (equity and debt, monthly and YTD), DII flows
- [ ] Mutual fund flows and SIP inflows (AMFI, monthly)
- [ ] Corporate bond spreads (AAA 5y over G-sec) if a free source exists
- [ ] Footnote stating the source and closing time for each row

## Must NOT include
- Download buttons for NSE/BSE index data (licensed, show-only)
- Intraday "live" quotes (we are end-of-day only)
- Stock tips, individual stocks, buy/sell language

## Series (planned)
nifty50_close, sensex_close, niftybank_close, niftyit_close, niftymid100_close, indiavix_close, gsec_2y_yield, gsec_5y_yield, gsec_10y_yield, gsec_30y_yield, usdinr_fbil, eurinr_fbil, gbpinr_fbil, jpyinr_fbil, brent_usd, gold_inr, fpi_equity_net, fpi_debt_net, dii_net, mf_sip_inflows

## Phase
1 (Nifty, Sensex, 10y, USD/INR, Brent, gold), 2 (page)
