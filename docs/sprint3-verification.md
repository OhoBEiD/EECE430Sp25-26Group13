# Sprint 3 — Manual verification walk-through

After `python manage.py migrate && python manage.py seed_demo && python manage.py runserver`, sign in as each demo user (`demo12345` for all) and confirm the role-specific behavior below.

## Visitor (no login)

1. Navigate to `/`. Hero says "Welcome to VolleyHub" with sign-in CTA. No injuries tile.
2. `/players/` lists all 15 players. Salary + contact columns show `—`. No Add / Edit / Delete / Export CSV buttons.
3. Click any player → detail loads with redacted salary/contact. No edit/delete buttons.
4. `/teams/` lists 3 teams. No Create button.
5. Click any team → detail loads. No Edit/Delete/Add Event.
6. `/teams/schedule/` shows all events.
7. `/injuries/` and `/analytics/` redirect to `/accounts/login/`.

## Player — `player_omar` / `demo12345`

1. Lands on `dashboard_player`. Hero says "Welcome back, Omar Tannous". Shows team (Beirut Blazers), open injuries (0), next 7 days events count.
2. Dock: Dashboard, Players, Teams, Schedule, Injuries, **My profile**, Sign out. **No Analytics tile.**
3. `/players/` shows only Beirut Blazers roster (5 players). Omar's row has a "You" badge. Salary + contact visible.
4. `/teams/` shows only Beirut Blazers. No Create / Edit / Delete CTAs.
5. `/teams/<cedars-pk>/` direct URL → 404.
6. `/me/` shows own player record + 14-day team events + (empty) injury history + recent stats.
7. `/injuries/` shows empty list (Omar has no injuries).
8. `/analytics/` direct URL works → shows Omar as the only selectable player. Click → analytics dashboard. No "Record Stats" button.
9. `/analytics/<other-player>/` direct URL → 403.

## Coach — `coach_ahmad` / `demo12345`

1. Lands on `dashboard_coach`. One tile per coached team (Beirut Blazers): players, active injuries, next sessions.
2. Dock includes **Coach console** (`/coach/`) and Analytics.
3. `/coach/` shows the coached-team console with roster, active injuries, upcoming events, "+ Add event" CTA.
4. `/players/` shows only Beirut Blazers roster. Edit button visible per row, no Delete (manager-only).
5. `/players/player/<cedars-player>/edit/` → 403.
6. `/teams/` shows only Beirut Blazers. Edit visible, no Create.
7. `/teams/<blazers-pk>/edit/` → form opens; coach picker is **disabled** (only managers can reassign).
8. `/teams/<blazers-pk>/event/add/` → event creation form.
9. `/injuries/create/` → form's player picker contains only Blazers roster. Saving sets `reported_by_user = coach_ahmad`.
10. `/analytics/<blazers-player>/record/` → form opens; saves with `recorded_by = coach_ahmad`.
11. `/analytics/<cedars-player>/record/` → 403.
12. CSV export hidden.

## Manager — `manager_sara` / `demo12345`

1. Lands on `dashboard_manager`. Full club aggregates + CSV/Add CTAs.
2. Dock: everything except Coach console, My profile, Users & roles, Django admin.
3. Full CRUD on every team / player / injury / event.
4. Click "⤓ Export player roster (CSV)" → file downloads.
5. `/admin-ui/users/` → 403.

## Scout — `scout_layla` / `demo12345`

1. Lands on `dashboard_scout`. Aggregates show injury count without clinical detail.
2. Dock: same as manager (no admin tiles).
3. `/players/` shows all 15. Salary + contact = `—`. No Edit / Delete / CSV.
4. `/injuries/` lists all rows. Click any detail → clinical notes show "— Clinical notes redacted for scouts —".
5. `/analytics/<any>/` → fully visible, no Record button.
6. POST `/injuries/<pk>/edit/` directly → 403.

## Admin — `admin_volleyhub` / `demo12345`

1. Lands on `dashboard_admin`. Manager view + "Users & roles" tile.
2. Dock includes **Users & roles** (`/admin-ui/users/`) and Django admin.
3. `/admin-ui/users/` shows table of all users with role + linked player + coached teams.
4. Click "Edit role" on `player_omar` → form. Change role to `coach`, save → redirects to list. `player_omar` now appears in TeamForm coach picker.
5. `/admin/` opens Django admin. User detail page shows the inline `UserProfile` editor.

## Test suite

```bash
python manage.py test accounts
```

Should print `OK` with 26 tests.
