---
name: daily
product: daily-note
title: "Daily note, {{nifty50_close.latest_period}}"
trigger: nifty50_close
trigger_weekdays_only: true
views: [nifty50_close, sensex_close, indiavix_close, usdinr_ref, gsec_10y_yield, brent_usd, brent_inr]
calendar: true
---
**Markets.** The Nifty closed at {{nifty50_close.latest}}, {{nifty50_close.pct_phrase}} since {{nifty50_close.prev_period}}, and the Sensex at {{sensex_close.latest}} ({{sensex_close.pct_phrase}}). India VIX was {{indiavix_close.latest}}. The rupee's reference rate was {{usdinr_ref.latest}} per US dollar on {{usdinr_ref.latest_period}}, {{usdinr_ref.pct_phrase}} since {{usdinr_ref.prev_period}} (a higher rate means a weaker rupee). The benchmark ten-year government bond yield was {{gsec_10y_yield.latest}} on {{gsec_10y_yield.latest_period}}. Brent crude settled at US$ {{brent_usd.latest}} a barrel on {{brent_usd.latest_period}} (₹ {{brent_inr.latest}} at the reference rate).

**Data released today:** {{calendar.today}}.

**Coming up:** {{calendar.next}}.

[Markets page](/markets/) · [Release calendar](/calendar/)
