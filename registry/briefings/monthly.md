---
name: monthly
product: monthly-briefing
title: "The month, to {{today.month}}"
trigger_monthday: 1
calendar: true
views: [nifty50_close, sensex_close, usdinr_ref, gsec_10y_yield, brent_usd, fx_reserves_total, repo_rate, liquidity_surplus,
        cpi_headline_inflation, cpi_core_index:yoy, cpi_food_bev_index:yoy, wpi_headline_index:yoy, iip_general_growth,
        core_overall_index:yoy, gst_gross_collections, merch_trade_balance, merch_exports:yoy, plfs_ur_monthly,
        scb_credit_growth, gdp_real_growth, cga_fiscal_deficit_pct_be]
---
**Markets over the month.** The Nifty ended at {{nifty50_close.latest}} ({{nifty50_close.month_phrase}} over the month) and the Sensex at {{sensex_close.latest}} ({{sensex_close.month_phrase}}). The rupee's reference rate was {{usdinr_ref.latest}} per US dollar ({{usdinr_ref.month_phrase}}). The ten-year government bond yield was {{gsec_10y_yield.latest}} and Brent crude {{brent_usd.latest}} ({{brent_usd.month_phrase}}). Foreign exchange reserves stood at {{fx_reserves_total.latest}} ({{fx_reserves_total.month_phrase}}).

**Prices.** CPI inflation was {{cpi_headline_inflation.latest}} in {{cpi_headline_inflation.latest_period}}, against {{cpi_headline_inflation.prev}} the month before and RBI's target of {{const.rbi_inflation_target}}. Core inflation was {{cpi_core_index:yoy.latest}} and food and beverages {{cpi_food_bev_index:yoy.latest}}. Wholesale prices rose {{wpi_headline_index:yoy.latest}} on a year earlier.

**Activity and jobs.** Industrial production grew {{iip_general_growth.latest}} in {{iip_general_growth.latest_period}} and the eight core industries {{core_overall_index:yoy.latest}}. GST collections were {{gst_gross_collections.latest}} in {{gst_gross_collections.latest_period}}. The unemployment rate was {{plfs_ur_monthly.latest}} in {{plfs_ur_monthly.latest_period}}. The latest quarter's real GDP growth is {{gdp_real_growth.latest}} ({{gdp_real_growth.latest_period}}).

**Money, trade and the budget.** The repo rate is {{repo_rate.latest}}; bank credit grew {{scb_credit_growth.latest}} on a year earlier ({{scb_credit_growth.latest_period}}), and banking liquidity was {{liquidity_surplus.latest}} on {{liquidity_surplus.latest_period}}. The merchandise trade balance was {{merch_trade_balance.latest}} in {{merch_trade_balance.latest_period}}, with exports {{merch_exports:yoy.latest}} on a year earlier. The Centre's fiscal deficit reached {{cga_fiscal_deficit_pct_be.latest}} of the year's Budget Estimate by {{cga_fiscal_deficit_pct_be.latest_period}}.

**Released last month:** {{calendar.past_month}}.

**Coming up:** {{calendar.next_month}}.

[Home](/) · [Release calendar](/calendar/)
