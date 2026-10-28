---
name: mpc
title: "RBI policy decision, {{repo_rate.latest_period}}"
trigger_calendar: "MPC policy decision"
views: [repo_rate, sdf_rate, msf_rate, crr, cpi_headline_inflation, cpi_core_index:yoy, gdp_real_growth]
calendar: true
---
**The policy repo rate is {{repo_rate.latest}} after the Monetary Policy Committee's decision**, {{repo_rate.bp_phrase}} from {{repo_rate.prev}} (the rate in force on {{repo_rate.prev_period}}). The standing deposit facility rate is {{sdf_rate.latest}} and the marginal standing facility rate {{msf_rate.latest}}; the cash reserve ratio is {{crr.latest}} ({{crr.bp_phrase}}).

The decision came with headline CPI inflation at {{cpi_headline_inflation.latest}} in {{cpi_headline_inflation.latest_period}} against RBI's target of {{const.rbi_inflation_target}}, core inflation at {{cpi_core_index:yoy.latest}}, and real GDP growth of {{gdp_real_growth.latest}} in {{gdp_real_growth.latest_period}}.

The committee's statement, including its vote and stance, is on [RBI's website](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx). Next scheduled decision: {{calendar.next_highlight}}.

[Money & banking page](/money/)
