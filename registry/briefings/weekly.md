---
name: weekly
product: weekly-briefing
title: "The week, to {{nifty50_close.latest_period}}"
trigger_weekday: 5   # Saturday
calendar: true
views: [nifty50_close, sensex_close, indiavix_close, usdinr_ref, gsec_10y_par_fbil, wacr, fx_reserves_total, brent_usd, cpi_headline_inflation, cpi_core_index:yoy, gdp_real_growth, iip_general_growth, plfs_ur_monthly, merch_trade_balance, scb_credit_growth, repo_rate]
---
**Markets over the week.** The Nifty ended at {{nifty50_close.latest}} ({{nifty50_close.week_phrase}} on the week) and the Sensex at {{sensex_close.latest}} ({{sensex_close.week_phrase}}). India VIX finished at {{indiavix_close.latest}}. Brent crude was {{brent_usd.latest}} ({{brent_usd.week_phrase}}).

**Money and the rupee.** The policy repo rate is {{repo_rate.latest}}. In the latest week of RBI data (to {{wacr.latest_period}}) the weighted average call rate was {{wacr.latest}} ({{wacr.week_phrase}}) and the ten-year government bond par yield {{gsec_10y_par_fbil.latest}} ({{gsec_10y_par_fbil.week_phrase}}). Foreign exchange reserves were {{fx_reserves_total.latest}} ({{fx_reserves_total.week_phrase}}). The rupee's reference rate was {{usdinr_ref.latest}} per US dollar on {{usdinr_ref.latest_period}}.

**Scheduled releases this week:** {{calendar.past_week}}.

**Where things stand.** Headline CPI inflation {{cpi_headline_inflation.latest}} ({{cpi_headline_inflation.latest_period}}); core {{cpi_core_index:yoy.latest}}. Real GDP growth {{gdp_real_growth.latest}} ({{gdp_real_growth.latest_period}}). Industrial production growth {{iip_general_growth.latest}} ({{iip_general_growth.latest_period}}). Unemployment {{plfs_ur_monthly.latest}} ({{plfs_ur_monthly.latest_period}}). Merchandise trade balance {{merch_trade_balance.latest}} ({{merch_trade_balance.latest_period}}). Bank credit growth {{scb_credit_growth.latest}} ({{scb_credit_growth.latest_period}}).

**Scheduled next week:** {{calendar.next_week}}.

[Home](/) · [Release calendar](/calendar/)
