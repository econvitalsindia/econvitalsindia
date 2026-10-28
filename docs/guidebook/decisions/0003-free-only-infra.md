# 0003 · Free-only infrastructure

**Date:** 2026-10-28 · **Status:** accepted

**Decision:** GitHub Actions (free tier), Cloudflare Pages + Access (free), newsletter on a free tier. Sources that block US IPs run via `make india-update` from a machine in India.
**Cost of the choice:** a few minutes of manual work per day; private-repo Actions capped at 2,000 min/month.
**Revisit:** at launch (public repo → unlimited minutes), or if the manual queue exceeds about 10 minutes/day. Then use a self-hosted runner on an always-on Mac (still free) or a small Indian VPS.
