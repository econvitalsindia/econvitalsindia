---
name: cpi
title: "CPI inflation, {{cpi_headline_inflation.latest_period}}"
trigger: cpi_headline_inflation
views: [cpi_headline_inflation, cpi_core_index:yoy, cpi_food_bev_index:yoy, cpi_fuel_index:yoy, cpi_rural_index:yoy, cpi_urban_index:yoy]
---
**Headline consumer price inflation was {{cpi_headline_inflation.latest}} in {{cpi_headline_inflation.latest_period}}**, {{cpi_headline_inflation.change_phrase}} from {{cpi_headline_inflation.prev}} in {{cpi_headline_inflation.prev_period}}, according to MoSPI. A year earlier it was {{cpi_headline_inflation.year_ago}}. RBI's target is {{const.rbi_inflation_target}}, with a tolerance band of {{const.rbi_tolerance_band}}.

Core inflation, which excludes food and fuel (RBI's definition; our calculation from MoSPI's indices), was {{cpi_core_index:yoy.latest}}, {{cpi_core_index:yoy.change_phrase}} from the previous month. Inflation in food and beverages was {{cpi_food_bev_index:yoy.latest}} ({{cpi_food_bev_index:yoy.change_phrase}}) and in fuel {{cpi_fuel_index:yoy.latest}} ({{cpi_fuel_index:yoy.change_phrase}}).

By area, rural inflation was {{cpi_rural_index:yoy.latest}} and urban inflation {{cpi_urban_index:yoy.latest}}.

[Inflation page](/inflation/) · [Contributions by division](/inflation/detail/)
