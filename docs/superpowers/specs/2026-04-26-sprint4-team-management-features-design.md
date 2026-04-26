# Sprint 4 — Team Management Features (Design Spec)

**Date:** 2026-04-26
**Status:** Approved (brainstorming complete; awaiting implementation plan)
**Predecessor:** Sprint 3 (`v0.3-sprint3`) shipped 6-role enforcement + scoped data access
**Estimated size:** ~28 pts across 7 PRs

## Context

VolleyHub already has six enforced user roles (visitor / player / coach / manager / scout / admin), per-role dashboards, scoped querysets, decorators, predicates, template tags, and PII redaction (Sprint 3, see `README.md` and `docs/sprint3-verification.md`). The next thing the user wants is to make VolleyHub feel like a real *team management* platform, not just a roster + injury tracker.

From a 15-feature wishlist, four were prioritized and nine were deferred:

**Sprint 4 (this spec):**
1. Player Performance Dashboard — comprehensive per-player rollup
2. Coach Feedback System — event-tied private notes
3. Attendance Tracking — present/absent/late/excused per event
4. Match Lineup Builder — starting 7 (Setter / 2 OH / 2 MB / Opposite / Libero) per Game

**Deferred (later sprints / backlog):**
- #3 Training Schedule Calendar (we already have events; calendar UI is polish)
- #5 Player Availability Form (player-side counterpart of attendance)
- #7 Team Announcements
- #8 Skill Rating System (Sprint 4 derives strengths/weaknesses from PlayerStats instead)
- #9 Player Goals
- #10 Wellness Status
- #11 Match Results & Statistics
- #12 Photo Gallery
- #13 Player of the Week
- #14 Notifications System

Sprint 4 is sized to fit the same 6-8-PR rhythm Sprint 3 used. Player Performance Dashboard is the *consumer* of the other 3 features and is built last (PR 6).

## Design decisions

1. **Three new Django apps**: `attendance`, `feedback`, `lineups`. Each owns its own model + view + form + template + migrations + tests. Matches the existing `players / teams / injuries / analytics / accounts` pattern. Avoids piling more onto `teams/`.
2. **All three new models reference `Event` (FK)**. Attendance and Feedback are post-event artifacts; Lineup is a pre-event artifact. Anchoring everything to events gives a natural "event review" workflow on `/teams/event/<pk>/...`.
3. **Coach Feedback is event-tied** (not freeform). Pairs naturally with Attendance — both are "after-event" actions on the same Event. A freeform-notes feature can be added later if needed.
4. **Lineup is the starting 7** (1 Setter, 2 OH, 2 MB, 1 Opposite, 1 Libero) — matches standard volleyball. No substitution tracking, no per-set lineups, no bench order. Bench is implicitly "anyone on roster not in the lineup."
5. **Player Performance Dashboard expands `/analytics/<pk>/`** rather than creating a new route. The existing stats page becomes the canonical performance page; new sections (Attendance, Feedback, Injuries, Strengths/Weaknesses) layer on top.
6. **Strengths/Weaknesses are auto-derived** from PlayerStats (top-2 / bottom-2 of latest stat line). No new model. When `Skill Ratings` (#8) lands later, it can replace this derivation.
7. **Permission shape reuses Sprint 3 infrastructure**: `role_required`, `team_coach_required`, `players_for(user)`, `teams_for(user)` — no new authorization primitives needed.
8. **Scout cannot see Coach Feedback**. Feedback is a coach↔player private channel. Manager and admin can see all feedback (oversight). Scout can see attendance % and lineups (those are operational facts, not private opinion).
9. **24-hour edit window on feedback**. Prevents post-hoc rewriting after a player reads it. Implemented as a `can_edit_feedback(user, feedback)` predicate; older feedback is read-only via UI (delete still allowed for the original coach + manager + admin).

## Data model

### `attendance/models.py`

```python
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='attendance')
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='attendance')
    status = CharField(max_length=10, choices=STATUS_CHOICES)
    notes = TextField(blank=True)
    marked_by = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True)
    marked_at = DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('event', 'player')]
        indexes = [Index(fields=['player', 'status'])]
```

### `feedback/models.py`

```python
class Feedback(models.Model):
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='feedback')
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='feedback')
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, related_name='feedback_written')
    body = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [Index(fields=['player', '-created_at'])]
```

### `lineups/models.py`

```python
class LineupSlot(models.Model):
    POSITION_CHOICES = [
        ('SETTER', 'Setter'),
        ('OH1',    'Outside Hitter 1'),
        ('OH2',    'Outside Hitter 2'),
        ('MB1',    'Middle Blocker 1'),
        ('MB2',    'Middle Blocker 2'),
        ('OPP',    'Opposite'),
        ('LIBERO', 'Libero'),
    ]
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='lineup_slots')
    position = CharField(max_length=10, choices=POSITION_CHOICES)
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='lineup_slots')

    class Meta:
        unique_together = [('event', 'position'), ('event', 'player')]

    def clean(self):
        if self.event.event_type not in ('Game', 'Tournament'):
            raise ValidationError('Lineups are only for Game or Tournament events.')
        if self.player.team_id != self.event.team_id:
            raise ValidationError("Player must be on the event's team.")
```

## Per-feature scope

### 1. Attendance Tracking

**In:**
- `attendance` app with `Attendance` model + migrations + admin + tests.
- Event detail page (`teams/templates/teams/team_detail.html` consumer; or new section template) gains an "Attendance" form for coach/manager/admin: roster of the event's team rendered with a status dropdown per row + optional note. Bulk save in one POST.
- Attendance card visible on event detail to anyone who can see the team (read-only): "Attendance: 12 present / 1 late / 2 absent / 0 excused".
- `/me/` shows "My attendance: 88% (15/17 sessions)".
- `/coach/` shows per-team aggregate "Beirut Blazers attendance (last 30 days): 92%".
- `/analytics/<pk>/` (Performance Dashboard) shows player's attendance % card.

**Out (defer):**
- Player self-marking availability before the event (#5 — Sprint 5 candidate).
- Email reminders for absences.
- Auto-mark "absent" for past events without records (would mass-create rows for legacy events).

**Permissions:**
- Mark/edit: `team_coach_required` on the event's team OR manager/admin.
- Read: scoped via existing `injuries_for`-style approach. Player sees own attendance only; coach sees own team's; manager/scout/admin see all.

### 2. Coach Feedback

**In:**
- `feedback` app with `Feedback` model + migrations + admin + tests.
- Event detail page gains a "Feedback" section for coach/manager/admin: one textarea per roster player; coach types a note, hits Save → creates Feedback row.
- Player sees their own feedback chronologically on `/me/` grouped by event.
- Player Performance Dashboard shows last 3 feedback entries (only visible to player-self / coach-of-team / manager / admin — *not* scout).
- Coach can edit/delete their own feedback within 24h. After 24h, edit is hidden (delete still available to original coach + manager + admin).

**Out:**
- Player reactions/replies to feedback.
- Rich text or attachments.
- Notifications when new feedback arrives.

**Permissions:**
- Write/edit: coach of the event's team + manager + admin (with 24h window for edit).
- Delete: coach who wrote it (any time) + manager + admin.
- Read: `can_view_feedback(user, feedback)` predicate — coach who wrote OR linked player OR manager/admin. **Scout = NO.**

### 3. Match Lineup Builder

**In:**
- `lineups` app with `LineupSlot` model + migrations + admin + tests.
- Only Event of type `Game` or `Tournament` shows the lineup section.
- Single-page form on event detail with 7 selects (one per position) scoped to roster of the event's team.
- Validation: player must be on the event's team; can't double-assign one player to two slots (DB unique constraint + form clean).
- Lineup card on event detail visible to anyone who can see the team.
- `/me/` shows "Starting at OH1 vs Tripoli Spikers (Apr 28)" badge for the player.
- `/players/player/<pk>/` shows "Starting at X" badge in the relevant upcoming-event row.

**Out:**
- Substitution tracking during the match.
- Per-set lineups (one lineup per event).
- Auto-suggestions / lineup history templates.

**Permissions:**
- Write: `team_coach_required` on the event's team + manager + admin.
- Read: public to anyone who can see the team (visitor included, since lineups are typically posted publicly before games).

### 4. Player Performance Dashboard (rollup on `/analytics/<pk>/`)

**In:** Extends the existing `analytics_dashboard` view with the following new sections, conditionally rendered per role:
- **Attendance card** (bar + %): visible to player-self / coach-of-team / manager / scout / admin.
- **Recent feedback** (last 3): visible to player-self / coach-of-team / manager / admin. Scout sees a "Coach feedback redacted for scouts" placeholder.
- **Active injuries card**: pulled from existing `Injury` model; visible to player-self / coach / manager / scout / admin (no body).
- **Strengths**: top-2 categories from latest PlayerStats.
- **Areas to improve**: bottom-2 categories from latest PlayerStats.
- For coach viewing one of their players: prominent "+ Record stats" / "+ Add feedback" CTAs.

**Out:**
- Goals (#9 deferred).
- Skill ratings as a separate model (#8 — Sprint 4 derives from PlayerStats).
- Coach-entered free-text strengths/weaknesses.

**Permissions:** unchanged from Sprint 3 — `self_player_or_role(coach, manager, scout, admin)`. Per-section role checks render or hide cards.

## PR sequence (~28 pts, 7 PRs)

| # | PR | Pts | Branch | Outcome |
|---|---|---|---|---|
| 1 | Attendance app foundation | 3 | `feat/sprint4-pr1-attendance-foundation` | `Attendance` model + migration + admin + seed_demo back-populates a few rows. Tests pass. Nothing visible yet. |
| 2 | Attendance UI on event detail + dashboards | 5 | `feat/sprint4-pr2-attendance-ui` | Coach can mark attendance after a session; player sees their attendance % on `/me/`; coach sees team aggregate on `/coach/`. |
| 3 | Feedback app + UI + 24h edit window | 5 | `feat/sprint4-pr3-feedback` | Coach writes per-event feedback; player reads on `/me/`; scout cannot see; 24h edit window enforced via predicate + template. |
| 4 | Lineups app foundation | 3 | `feat/sprint4-pr4-lineups-foundation` | `LineupSlot` model + migration + admin; `seed_demo` populates one upcoming Game with a sample lineup. |
| 5 | Lineup builder UI + player badges | 5 | `feat/sprint4-pr5-lineup-builder` | Coach builds a lineup; player sees "Starting at X" badge on `/me/` and player profile. |
| 6 | Performance Dashboard rollup | 5 | `feat/sprint4-pr6-performance-dashboard` | `/analytics/<pk>/` gains Attendance %, Recent Feedback (gated, no scout), Active Injuries, derived Strengths/Weaknesses. Coach gets quick-action CTAs. |
| 7 | Polish + docs + verification | 2 | `feat/sprint4-pr7-cleanup` | README updates (new apps, features matrix); `docs/sprint4-verification.md` walk-through; `docs/sprint4-retro.md` template; tag `v0.4-sprint4`. |

**Total: 28 pts.** PR 1+2 ship attendance vertically; PR 3 ships feedback vertically; PR 4+5 ship lineups vertically; PR 6 consumes everything.

## Verification (sketched — full version lands in `docs/sprint4-verification.md` from PR 7)

After `python manage.py migrate && python manage.py seed_demo && python manage.py runserver`, walk each role through:

- **Visitor**: opens an upcoming Game event detail → sees the lineup card (read-only). Attendance & feedback sections are hidden.
- **Player** (`player_omar`): `/me/` shows own attendance % + per-event feedback list + "Starting at OH1" badge if applicable; `/analytics/<own-pk>/` shows the full Performance Dashboard with all five sections; cannot mark attendance / write feedback / edit lineup.
- **Coach** (`coach_ahmad`): on Beirut Blazers event detail, fills attendance form, writes feedback for selected players, builds lineup for an upcoming game; can edit own feedback within 24h.
- **Manager** (`manager_sara`): full read/write across all teams; sees all feedback on the dashboard.
- **Scout** (`scout_layla`): sees attendance %, lineup card; **does NOT** see Coach Feedback section anywhere — placeholder shown on dashboard.
- **Admin** (`admin_volleyhub`): everything works; can role-assign new coaches via `/admin-ui/users/`.

Plus automated test pass:
```bash
python manage.py test accounts attendance feedback lineups
```

## Open questions / risks

1. **Attendance UI on practice events without a roster snapshot**: a practice event today doesn't store "expected attendees" — it's just an Event tied to a Team. The roster used for marking is `team.players.all()` at the time of marking. If a player joins/leaves the team between the event date and when attendance is marked, the roster shown could miss them. Sprint 4 accepts this; a later sprint can add an `Event.snapshot_roster` denormalization if needed.
2. **Feedback 24h window** is wall-clock, not since-event-date. A coach writing feedback the next morning has a 24h window from the *write* time. Simple and forgiving.
3. **Lineup uniqueness on edit**: the "swap two players" UX requires either a transactional save (recommended) or temporary "unassign first, assign second" workflow. PR 5 will use form-level validation to swap atomically.
4. **Attendance % computation**: For a player, the denominator is the number of past events where *that player* has an `Attendance` row (any status); the numerator is the count of those rows where `status == 'present'` or `'late'`. Players without rows for an event aren't penalized — events with no marking just don't count. The team aggregate on `/coach/` uses the same shape, summed across players over the last 30 days.
5. **Performance Dashboard with no PlayerStats**: existing analytics view already handles the empty state; new sections also degrade gracefully (Attendance shows "—", Feedback shows "No feedback yet", etc.).

## Critical files to be modified or created

**Create:**
- `attendance/` (new app) — `models.py`, `admin.py`, `apps.py`, `views.py`, `forms.py`, `urls.py`, `migrations/0001_initial.py`, `tests.py`, `permissions.py`, `querysets.py`
- `feedback/` (new app) — same shape; `permissions.py` includes `can_view_feedback`, `can_edit_feedback` (24h window)
- `lineups/` (new app) — same shape; model has `clean()` validation; form swaps atomically
- `templates/attendance/_card.html`, `_form.html` (partials included from event detail)
- `templates/feedback/_section.html`, `_form.html`
- `templates/lineups/_card.html`, `_form.html`
- `docs/sprint4-verification.md` (PR 7)
- `docs/sprint4-retro.md` (PR 7)

**Modify:**
- [`volleyhub/settings.py`](volleyhub/volleyhub/settings.py) — add three apps to `INSTALLED_APPS`
- [`volleyhub/urls.py`](volleyhub/volleyhub/urls.py) — mount the three apps' urlconfs (or attach views directly to event URLs)
- [`teams/views.py`](volleyhub/teams/views.py) `team_detail` — add attendance/feedback/lineup context bundles
- [`templates/teams/team_detail.html`](volleyhub/templates/teams/team_detail.html) — include the new partials per event
- [`analytics/views.py`](volleyhub/analytics/views.py) `analytics_dashboard` — add new context (attendance %, recent feedback, active injuries, strengths/weaknesses)
- [`templates/analytics/dashboard.html`](volleyhub/templates/analytics/dashboard.html) — render the four new cards
- [`templates/dashboard_player.html`](volleyhub/templates/dashboard_player.html), [`dashboard_coach.html`](volleyhub/templates/dashboard_coach.html) — surface attendance %
- [`templates/accounts/me.html`](volleyhub/templates/accounts/me.html) — add per-event feedback list and lineup badge
- [`players/management/commands/seed_demo.py`](volleyhub/players/management/commands/seed_demo.py) — populate sample attendance + feedback + one lineup
- [`README.md`](volleyhub/README.md) — extend Apps list + add Sprint 4 row to velocity table

## Sequencing the implementation plan

After this spec is approved by the user, I will invoke the `superpowers:writing-plans` skill to produce a detailed PR-by-PR implementation plan that mirrors the Sprint 3 cadence. Each PR will include verification steps and test instructions.
