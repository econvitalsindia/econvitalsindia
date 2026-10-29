"""India and emerging-market peers: policy rates, CPI inflation and GDP growth.

The IMF DataMapper API refuses scripted requests (403), so:
  - policy rates, monthly, end of period: BIS WS_CBPOL
      https://stats.bis.org/api/v1/data/WS_CBPOL/M.<areas>/all?format=csv
  - CPI inflation, monthly, % on a year earlier: BIS WS_LONG_CPI, unit 771
      https://stats.bis.org/api/v1/data/WS_LONG_CPI/M.<areas>.771/all?format=csv
  - real GDP growth, annual %: World Bank NY.GDP.MKTP.KD.ZG
      https://api.worldbank.org/v2/country/<iso3;...>/indicator/NY.GDP.MKTP.KD.ZG?format=json
Each source's own definitions apply (e.g. the World Bank's year for India may differ from
the financial years on our Growth page). Panels: entity = country.

Series: peer_policy_rate, peer_cpi_inflation (monthly), peer_gdp_growth (annual).
"""
from __future__ import annotations

import io
import json

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

# BIS area code -> (World Bank ISO3, name on the site)
PEERS = {"IN": ("IND", "India"), "CN": ("CHN", "China"), "ID": ("IDN", "Indonesia"), "BR": ("BRA", "Brazil"),
         "ZA": ("ZAF", "South Africa"), "MX": ("MEX", "Mexico"), "PH": ("PHL", "Philippines"),
         "TH": ("THA", "Thailand"), "MY": ("MYS", "Malaysia")}
AREAS = "+".join(PEERS)
START = "2015-01"
BIS_POLICY = f"https://stats.bis.org/api/v1/data/WS_CBPOL/M.{AREAS}/all?format=csv&startPeriod={START}"
BIS_CPI = f"https://stats.bis.org/api/v1/data/WS_LONG_CPI/M.{AREAS}.771/all?format=csv&startPeriod={START}"
WB_GDP = ("https://api.worldbank.org/v2/country/" + ";".join(v[0] for v in PEERS.values())
          + "/indicator/NY.GDP.MKTP.KD.ZG?format=json&date=2010:2030&per_page=500")


def bis_rows(content: bytes, sid: str) -> list[dict]:
    df = pd.read_csv(io.BytesIO(content), dtype={"TIME_PERIOD": str})
    df = df[df["REF_AREA"].isin(PEERS) & df["OBS_VALUE"].notna()]
    return [{"series_id": sid, "entity": PEERS[a][1], "period": f"{t}-01", "value": round(float(v), 3)}
            for a, t, v in zip(df["REF_AREA"], df["TIME_PERIOD"], df["OBS_VALUE"])]


def wb_rows(content: bytes) -> list[dict]:
    meta, data = json.loads(content)
    name = {iso3: n for iso3, n in PEERS.values()}
    return [{"series_id": "peer_gdp_growth", "entity": name[r["countryiso3code"]], "period": f"{r['date']}-01-01",
             "value": round(float(r["value"]), 2)} for r in data or [] if r["value"] is not None and r["countryiso3code"] in name]


class IntlPeers(Source):
    name = "intl_peers"
    panel = True
    series_ids = ("peer_policy_rate", "peer_cpi_inflation", "peer_gdp_growth")

    def fetch(self) -> list[Raw]:
        return [fetch_raw(BIS_POLICY, suffix=".csv"), fetch_raw(BIS_CPI, suffix=".csv"), fetch_raw(WB_GDP, suffix=".json")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        policy, cpi, gdp = raws
        rows = bis_rows(policy.content, "peer_policy_rate") + bis_rows(cpi.content, "peer_cpi_inflation") + wb_rows(gdp.content)
        out = pd.DataFrame(rows)
        out["note"] = ""
        return out


SOURCE = IntlPeers()
