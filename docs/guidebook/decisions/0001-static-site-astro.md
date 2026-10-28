# 0001 · Static site with Astro + Observable Plot

**Date:** 2026-10-28 · **Status:** accepted

**Context:** We need a free, low-maintenance site that an RA can edit, with many charts and a blog.
**Decision:** Astro static build, Observable Plot for charts, data precomputed to JSON at build time.
**Alternatives:** Quarto (familiar to economists, but less flexible for dashboard layouts); Next.js (needs more JS skill, server features we don't need); Observable Framework (good fit, but uncertain maintenance).
**Consequences:** No runtime server, so anything "live" is end-of-day. Interactive tools must be client-side.
