# Sprint 1 Retrospective

**Dates:** 2026-04-14 (single-day sprint — calibration run)
**Planned:** 10 pts — issues #1, #2, #3, #6
**Completed:** 10 pts
**Velocity:** **10 pts**

## Completed stories

- [x] #1 Admin login/logout — 3 pts — PR #21
- [x] #2 `@login_required` on CRUD views — 2 pts — PR #22
- [x] #3 Search players by name — 3 pts — PR #23
- [x] #6 Paginate player list — 2 pts — PR #24

## What went well

- Picking 4 small, parallelizable stories made the Scrum workflow easy to exercise end-to-end.
- Reusing the existing `.glass-card-dark` / `.form-group-dark` / `.btn` / `.dock-item` CSS kept the login page and new controls visually consistent with the rest of VolleyHub.
- Django's built-in `django.contrib.auth` + `Paginator.get_page()` cut implementation time substantially — no custom auth or pagination logic needed.
- PR-per-story discipline produced a clean merge history that tells the sprint story.

## What didn't go well

- `main` branch protection wasn't turned on at the start, so self-merges didn't exercise the review step authentically. Turn on protection before Sprint 2.
- Teammates weren't added as collaborators yet → no real code review happened. Block on this before Sprint 2 planning.

## Changes for Sprint 2

- Add teammates + lab instructor as collaborators **before** starting Sprint 2.
- Enable `main` branch protection (require PR + 1 approval) so every merge goes through review.
- Size Sprint 2 to ~11 pts (small stretch over measured velocity of 10).

## Velocity for Sprint 2 planning

Pick stories totaling ≈ 10 pts. Recommended batch from the product backlog: #4 (filter injuries, 3) + #8 (CSV player export, 3) + #11 (dashboard homepage, 5) = **11 pts**.
