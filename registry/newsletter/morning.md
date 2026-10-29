---
# The morning newsletter (pipelines/newsletter/morning.py).
# `views` are the facts the AI writer may use (every number in the email is one of these
# ledger tokens); the body below is the FALLBACK, sent as-is when the AI draft fails the
# checker twice or no ANTHROPIC_API_KEY is set. Same token rules as registry/briefings.
name: morning
product: morning-newsletter
subject: "India this morning, {{today.date}}"
views: [nifty50_close, sensex_close, indiavix_close, usdinr_ref, gsec_10y_yield, term_spread_10y_repo,
        brent_usd, gold_usd_oz, repo_rate, liquidity_surplus, fpi_total_net, mf_net_inflow_equity,
        cpi_headline_inflation, cpi_core_index:yoy, cpi_food_bev_index:yoy, wpi_headline_index:yoy,
        gdp_real_growth, iip_general_growth, core_overall_index:yoy, plfs_ur_monthly,
        gst_gross_collections, gst_gross_growth, upi_volume:yoy, ewaybills_count:yoy,
        auto_pv_sales:yoy, fuel_consumption_total:yoy, scb_credit_growth, m3_growth,
        merch_trade_balance, merch_exports:yoy, fx_reserves_total, bop_remittances,
        cga_fiscal_deficit_pct_be]
calendar: true
---
**Markets.** The Nifty closed at {{nifty50_close.latest}} on {{nifty50_close.latest_period}} ({{nifty50_close.pct_phrase}} since {{nifty50_close.prev_period}}). The rupee's reference rate was {{usdinr_ref.latest}} per US dollar and the ten-year government bond yield {{gsec_10y_yield.latest}}. Brent crude was {{brent_usd.latest}}.

**Prices and policy.** CPI inflation was {{cpi_headline_inflation.latest}} in {{cpi_headline_inflation.latest_period}}, against RBI's target of {{const.rbi_inflation_target}}. The repo rate is {{repo_rate.latest}}.

**Activity.** Real GDP grew {{gdp_real_growth.latest}} on a year earlier in {{gdp_real_growth.latest_period}}. Industrial production grew {{iip_general_growth.latest}} in {{iip_general_growth.latest_period}}, and GST collections were {{gst_gross_collections.latest}} in {{gst_gross_collections.latest_period}}.

**New on the site since yesterday morning:** {{new.recent}}.

**Due today:** {{calendar.today}}. **Coming up:** {{calendar.next}}.
