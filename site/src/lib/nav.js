// The site menu: every page and every section a reader might look for.
// When you add a page or an <h2> section, add it here too (guidebook 05-pages/README.md).
// Section links use fixed ids set on the <h2> (id="..."), never ids derived from text that
// changes with the data (e.g. "Consumer prices, Sep 2026").
// `key` matches the `current` prop pages pass to Base, to underline the active menu.

export const topics = [
  { key: "growth", label: "Growth", href: "/growth/", items: [
    ["GDP growth", "/growth/"],
    ["Growth by sector", "/growth/#by-sector"],
    ["Growth by spending component", "/growth/#by-spending"],
    ["Nominal and real", "/growth/#nominal-real"],
    ["Forecasts and sentiment", "/growth/#forecasts"],
  ] },
  { key: "inflation", label: "Inflation", href: "/inflation/", items: [
    ["Headline and core CPI", "/inflation/"],
    ["What is driving inflation", "/inflation/#drivers"],
    ["Consumer prices by group", "/inflation/#cpi-table"],
    ["How core CPI is built", "/inflation/#core-cpi"],
    ["Rural and urban", "/inflation/#rural-urban"],
    ["Wholesale prices (WPI)", "/inflation/#wpi"],
    ["Households' inflation expectations", "/inflation/#expectations"],
    ["CPI for industrial workers", "/inflation/#cpi-iw"],
    ["CPI by division, detail", "/inflation/detail/"],
  ] },
  { key: "jobs", label: "Jobs", href: "/jobs/", items: [
    ["Latest months (PLFS)", "/jobs/#latest"],
    ["Longer run", "/jobs/#longer-run"],
    ["Concepts", "/jobs/#concepts"],
  ] },
  { key: "activity", label: "Activity", href: "/activity/", items: [
    ["Industrial production (IIP)", "/activity/"],
    ["IIP by sector and use", "/activity/#iip-detail"],
    ["Core industries", "/activity/#core-industries"],
    ["Electricity demand", "/activity/#electricity"],
    ["Vehicle sales", "/activity/#vehicles"],
    ["Fuel consumption", "/activity/#fuel"],
  ] },
  { key: "money", label: "Money", href: "/money/", items: [
    ["Policy rates and the call rate", "/money/"],
    ["MPC decisions and votes", "/money/#decisions"],
    ["Liquidity", "/money/#liquidity"],
    ["Bank credit and deposits", "/money/#credit"],
    ["Money supply (M3)", "/money/#money-supply"],
    ["Rates, recent weeks", "/money/#rates-table"],
    ["MPC Speak: hawkish or dovish?", "/money/mpc-speak/"],
  ] },
  { key: "markets", label: "Markets", href: "/markets/", items: [
    ["Stocks, rupee, bonds, oil, gold", "/markets/"],
  ] },
  { key: "fiscal", label: "Fiscal", href: "/fiscal/", items: [
    ["Fiscal deficit and capex", "/fiscal/"],
    ["Union government accounts", "/fiscal/#accounts"],
    ["GST collections", "/fiscal/#gst"],
    ["Direct taxes and other tax heads", "/fiscal/#taxes"],
  ] },
  { key: "external", label: "External", href: "/external/", items: [
    ["Merchandise trade", "/external/#merchandise"],
    ["Services trade", "/external/#services"],
    ["Balance of payments", "/external/#bop"],
  ] },
  { key: "states", label: "States", href: "/states/", items: null },
];

export const more = [
  { key: "tools", label: "Tools", href: "/money/mpc-speak/", items: [
    ["MPC Speak", "/money/mpc-speak/"],
    ["Core CPI (ex food and fuel)", "/inflation/#core-cpi"],
    ["Inflation by division", "/inflation/detail/"],
    ["Brent crude in rupees", "/markets/"],
  ] },
  { key: "briefings", label: "Briefings", href: "/briefings/", items: [
    ["All briefings", "/briefings/"],
    ["RSS: all briefings", "/briefings/rss.xml"],
    ["RSS: release notes", "/briefings/release-notes.xml"],
    ["RSS: daily notes", "/briefings/daily.xml"],
  ] },
  { key: "calendar", label: "Calendar", href: "/calendar/", items: null },
  { key: "about", label: "About", href: "/about/", items: [
    ["About this site", "/about/"],
    ["Data and downloads", "/data/"],
    ["Methods and original measures", "/methods/"],
    ["Data status", "/status/"],
  ] },
];
