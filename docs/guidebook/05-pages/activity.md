# Activity (high-frequency indicators)

**Purpose:** What do the monthly and daily indicators say about momentum before GDP comes out?

## Must include
- [x] IIP: general, manufacturing, mining, electricity, and use-based (capital goods, consumer durables, non-durables, infrastructure/construction)
- [x] Eight core industries index and components
- [x] Power demand (Grid-India daily energy met, 7-day avg y/y; manual source, `make india-update`)
- [x] GST gross collections (on the Fiscal page) and e-way bills (`ewaybills_count`, `ewaybills_value`, from Jul 2018)
- [x] Auto: passenger vehicle, two- and three-wheeler sales (SIAM wholesale; PV from Apr 2023)
- [x] Auto: Vahan retail registrations, from FADA's monthly PDF (pipelines/sources/fada/retail.py; newest release wins)
- [x] Fuel consumption (PPAC): total, diesel, petrol, ATF, LPG (from Apr 2023)
- [ ] Rail freight loading
- [x] Domestic and international air passengers, air freight (AAI monthly traffic reports, from Jan 2025)
- [x] Digital pulse: UPI volume and value (y/y) via RBI Payment System Indicators. FASTag still to add (Phase 4)
- [ ] PMI manufacturing/services headline (cited only; licensed)
- [ ] (Deferred 2026-10-29: most indicators have under three years of growth history in our data, too short for a fair z-score) Heatmap: each indicator's latest y/y as a z-score vs its own history (Original, Phase 4; the India analogue of econvitals' "relative to past performance")

## Must NOT include
- PMI time series as a downloadable file (licensed)
- Raw daily series without smoothing on the main page (use 7-day averages; raw on detail page)

## Series (planned)
iip_general_index, iip_<component>_index, core8_index, power_energy_met, gst_gross_collections, ewaybills_count, ewaybills_value, pv_sales, tw_sales, diesel_consumption, petrol_consumption, rail_freight_loading, air_passengers_domestic, air_passengers_international, air_freight_total, upi_volume, upi_value, pmi_mfg_headline, pmi_services_headline

## Phase
1 (IIP, core8, GST, power, UPI), 2 (page)
