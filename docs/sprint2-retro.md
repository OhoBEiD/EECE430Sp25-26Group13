# Sprint 2 Retrospective

**Dates:** 2026-04-14 (back-to-back with Sprint 1 in calibration mode)
**Planned:** 11 pts — issues #4, #8, #11
**Completed:** 11 pts
**Velocity:** **11 pts** (planned a 10% stretch over Sprint 1's 10 pt velocity)

## Completed stories

- [x] #4 Filter injuries by status — 3 pts — PR #28
- [x] #8 Export player roster as CSV — 3 pts — PR #29
- [x] #11 Dashboard homepage — 5 pts — PR #30

## Velocity comparison

| Sprint | Planned | Completed | Delta |
|--------|---------|-----------|-------|
| 1 | 10 | 10 | 0 |
| 2 | 11 | 11 | 0 |

Two sprints at 100% completion suggests our estimates are calibrated for this codebase — a good state to be in before adding risk.

## What went well

- The #3 search pattern from Sprint 1 made #4's filter implementation straightforward; same query-string-as-state idea.
- #8 (CSV export) was smaller than estimated because Django's `HttpResponse` + `csv.writer` is two lines of setup. Could've been 2 pts.
- #11 (dashboard) was the biggest change — required restructuring the root URL so `/` serves the dashboard and `/players/` owns the roster. That went smoothly because every template already used `{% url 'name' %}` instead of hardcoded paths.
- UX polish between sprints (pagination button visibility, hero consistency, suppressed re-play animations) was done as bugfix PRs on main — kept sprint point counts honest.

## What didn't go well

- Still no real peer review: teammates weren't added as collaborators in time for Sprint 2.
- `main` branch protection still not enabled.

## Changes / observations for future work

- For the next sprint, enable branch protection and require one reviewer per PR.
- Consider splitting story estimation into "code" vs "template" effort: #8 was overestimated because we mentally lumped CSV + UI wiring together.
- Role-based access (#16) remains the biggest outstanding item — would unlock a real user-persona story for the assignment demo.

## Final state for the assignment

- **Two shippable increments** on `main`: `v0.1-sprint1`, `v0.2-sprint2`.
- **Measured velocity:** 10, 11 (stable).
- **Backlog health:** 20 stories scoped, 7 completed, 13 remaining for future sprints.
