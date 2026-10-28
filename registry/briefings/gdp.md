---
name: gdp
title: "GDP, {{gdp_real_growth.latest_period}}"
trigger: gdp_real_growth
views: [gdp_real_growth, gva_real_growth, gdp_nominal_growth, pfce_real_level:yoy, gfcf_real_level:yoy, gva_mfg_growth, gva_agri_growth]
---
**Real GDP grew {{gdp_real_growth.latest}} on a year earlier in {{gdp_real_growth.latest_period}}**, compared with {{gdp_real_growth.prev}} in {{gdp_real_growth.prev_period}}, according to MoSPI. Real gross value added grew {{gva_real_growth.latest}} and nominal GDP {{gdp_nominal_growth.latest}}.

On the spending side, private consumption grew {{pfce_real_level:yoy.latest}} and fixed investment {{gfcf_real_level:yoy.latest}} (our calculations from MoSPI's levels). Manufacturing value added grew {{gva_mfg_growth.latest}} and agriculture {{gva_agri_growth.latest}}.

[Growth page](/growth/)
