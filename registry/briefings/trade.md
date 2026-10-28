---
name: trade
title: "Merchandise trade, {{merch_trade_balance.latest_period}}"
trigger: merch_trade_balance
views: [merch_trade_balance, merch_exports, merch_imports, merch_exports:yoy, merch_imports:yoy]
---
**The merchandise trade balance was {{merch_trade_balance.latest}} in {{merch_trade_balance.latest_period}}**, against {{merch_trade_balance.year_ago}} a year earlier, according to the Department of Commerce's provisional figures.

Exports were {{merch_exports.latest}}, a change of {{merch_exports:yoy.latest}} on a year earlier, and imports {{merch_imports.latest}}, a change of {{merch_imports:yoy.latest}}.

[External page](/external/)
