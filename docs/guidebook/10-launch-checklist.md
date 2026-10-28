# 10 · Launch checklist (Phase 5)

## Identity and permission
- [ ] Email Jason Furman (Econvitals) about the project and the name. If the name isn't welcome, rename via `09-rebranding.md`
- [ ] Final name, logo and domain
- [ ] About page states independence (no affiliation with Econvitals, RBI or GoI)

## Legal
- [ ] Terms of use and privacy page
- [ ] Licence audit: every `downloadable: true` series is GODL or otherwise redistributable. Every `show-only` source is attributed
- [ ] Map boundaries are official (States page)

## Quality
- [ ] Zero overdue series for 7 consecutive days
- [ ] Every page checklist in `05-pages/` fully ticked for Phase 1–2 items
- [ ] Spot check: 30 random numbers vs official releases, 0 errors
- [ ] Mobile and desktop QA (`playbooks/qa-site.md`)
- [ ] Accessibility: colour contrast, alt text on charts (auto-generated from data)

## Infrastructure
- [ ] Repo public (unlimited Actions minutes), or stay private within the minute budget
- [ ] Remove Cloudflare Access
- [ ] Analytics (Cloudflare Web Analytics or Plausible; no cookies)
- [ ] Newsletter provider live, double opt-in, unsubscribe tested
- [ ] Social preview (OG) images

## People
- [ ] At least two people can run `make india-update` and approve briefings
- [ ] On-call rota for release days
