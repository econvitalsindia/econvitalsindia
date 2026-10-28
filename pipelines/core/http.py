"""HTTP helpers shared by every source.

Indian government servers have three recurring quirks handled here:
- they reject non-browser clients, so we always send browser headers;
- some (api.mospi.gov.in) need TLS legacy renegotiation, which OpenSSL 3
  disables by default;
- some (eaindustry.nic.in) send an incomplete certificate chain. Those are
  handled per source by supplying the missing intermediate, never by turning
  verification off.
"""
from __future__ import annotations

import hashlib
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from pipelines.core import Raw

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}
# Hosts that only speak TLS with legacy renegotiation enabled.
LEGACY_TLS_HOSTS = {"api.mospi.gov.in"}
# Seconds between requests to the same host; government servers are fragile.
POLITE_DELAY = 1.0
_last_hit: dict[str, float] = {}


def _ssl_context(host: str) -> ssl.SSLContext:
    """Default verifying context, plus legacy renegotiation for hosts that need it."""
    ctx = ssl.create_default_context()
    if host in LEGACY_TLS_HOSTS:
        ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)
    return ctx


def get(url: str, params: dict | None = None, retries: int = 3, timeout: float = 60) -> httpx.Response:
    """GET with browser headers, per-host politeness delay and retries on transient errors."""
    host = urlparse(url).hostname or ""
    wait = POLITE_DELAY - (time.monotonic() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with httpx.Client(headers=HEADERS, verify=_ssl_context(host), timeout=timeout,
                              follow_redirects=True) as client:
                r = client.get(url, params=params)
            _last_hit[host] = time.monotonic()
            if r.status_code >= 500 or r.status_code == 429:
                raise httpx.HTTPStatusError(f"HTTP {r.status_code}", request=r.request, response=r)
            r.raise_for_status()
            return r
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            last_err = e
            # 4xx other than 429 will not fix itself; fail fast.
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500 \
                    and e.response.status_code != 429:
                break
            time.sleep(2 ** attempt * 2)
    raise RuntimeError(f"GET {url} failed: {last_err}") from last_err


def fetch_raw(url: str, params: dict | None = None, suffix: str = ".json") -> Raw:
    """Download a URL and wrap it with its receipt."""
    r = get(url, params=params)
    return Raw(content=r.content, url=str(r.url), fetched_at=datetime.now(timezone.utc),
               sha256=hashlib.sha256(r.content).hexdigest(), suffix=suffix)
