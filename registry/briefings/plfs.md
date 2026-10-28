---
name: plfs
title: "Unemployment, {{plfs_ur_monthly.latest_period}}"
trigger: plfs_ur_monthly
views: [plfs_ur_monthly, plfs_ur_rural_monthly, plfs_ur_urban_monthly, plfs_ur_youth_monthly, plfs_lfpr_monthly, plfs_lfpr_female_monthly]
---
**The unemployment rate was {{plfs_ur_monthly.latest}} in {{plfs_ur_monthly.latest_period}}**, {{plfs_ur_monthly.change_phrase}} from {{plfs_ur_monthly.prev_period}}, according to MoSPI's monthly Periodic Labour Force Survey (people aged fifteen and over, current weekly status). A year earlier it was {{plfs_ur_monthly.year_ago}}.

Rural unemployment was {{plfs_ur_rural_monthly.latest}} and urban unemployment {{plfs_ur_urban_monthly.latest}}. Youth unemployment was {{plfs_ur_youth_monthly.latest}}. The labour force participation rate was {{plfs_lfpr_monthly.latest}} ({{plfs_lfpr_monthly.change_phrase}}), and for women {{plfs_lfpr_female_monthly.latest}}.

[Jobs page](/jobs/)
