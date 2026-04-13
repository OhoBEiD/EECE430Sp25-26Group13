#!/usr/bin/env bash
# Create labels + 20 product backlog issues for VolleyHub Sprint assignment.
# Requires: gh CLI authenticated, run from inside the repo.
#
# Usage:
#   bash scripts/create-backlog.sh

set -euo pipefail

echo "==> Creating labels (safe to re-run — existing labels skipped)"

create_label() {
  local name="$1" color="$2" desc="$3"
  gh label create "$name" --color "$color" --description "$desc" 2>/dev/null \
    || echo "   (label '$name' already exists)"
}

create_label "story"  "0366d6" "User story"
create_label "bug"    "d73a4a" "Something isn't working"
create_label "chore"  "cccccc" "Maintenance task"
create_label "P1"     "b60205" "Priority 1 — sprint 1 candidate"
create_label "P2"     "fbca04" "Priority 2"
create_label "P3"     "0e8a16" "Priority 3 — nice to have"
create_label "sprint-1" "5319e7" "Planned for sprint 1"
create_label "sprint-2" "5319e7" "Planned for sprint 2"

echo ""
echo "==> Creating 20 backlog issues"

create_issue() {
  local title="$1" body="$2" labels="$3"
  gh issue create --title "$title" --body "$body" --label "$labels" >/dev/null
  echo "   + $title"
}

create_issue "[3 pts] Admin login/logout" \
"As an admin, I can log in and out so unauthenticated users cannot modify data.

**Acceptance:**
- \`/accounts/login/\` renders a login form
- Successful login redirects home
- Logout link in the nav bar
- Uses Django's built-in \`django.contrib.auth\` views

**Touches:** \`volleyhub/volleyhub/urls.py\`, new \`templates/registration/login.html\`" \
"story,P1"

create_issue "[2 pts] Protect all CRUD views with @login_required" \
"As an admin, I want unauthenticated users blocked from create/edit/delete views so data can't be modified without auth.

**Acceptance:**
- Every create/edit/delete view in players/, teams/, injuries/, analytics/ requires login
- Unauthenticated user hitting a protected URL → redirected to \`/accounts/login/\`
- Read-only list/detail can stay open (PO decision)

**Depends on:** #1" \
"story,P1"

create_issue "[3 pts] Search players by name on list page" \
"As an admin, I can search the player list by name so I can find a player quickly.

**Acceptance:**
- Search input at the top of \`/\` (player list)
- Submitting filters by \`name__icontains\`
- Empty search returns all players

**Touches:** \`players/views.py::player_list\`, \`templates/players/player_list.html\`" \
"story,P1"

create_issue "[3 pts] Filter injuries by status" \
"As a coach, I can filter the injury list by status (Active / Recovering / Cleared) so I focus on current issues.

**Acceptance:**
- Dropdown or tabs for status
- Selecting a status filters the table
- 'All' option resets

**Touches:** \`injuries/views.py::injury_list\`, \`templates/injuries/injury_list.html\`" \
"story,P2"

create_issue "[2 pts] Filter teams by age group" \
"As an admin, I can filter the team list by age group (U14/U16/U18/Senior).

**Acceptance:**
- Dropdown selector for age group
- Filters the team list
- 'All' resets

**Touches:** \`teams/views.py::team_list\`, \`templates/teams/team_list.html\`" \
"story,P2"

create_issue "[2 pts] Paginate player list (10 per page)" \
"As an admin, I want paginated lists so large rosters stay readable.

**Acceptance:**
- Player list shows 10 per page
- Prev / Next / page numbers
- Combines with search (#3) without losing the query

**Touches:** \`players/views.py::player_list\`, template" \
"story,P1"

create_issue "[2 pts] Paginate injury list" \
"Same as #6 but for injuries.

**Acceptance:**
- 10 injuries per page
- Combines with status filter (#4) without losing the selection

**Touches:** \`injuries/views.py::injury_list\`, template" \
"story,P2"

create_issue "[3 pts] Export player roster as CSV" \
"As an admin, I can download the full player roster as CSV so I can share it offline.

**Acceptance:**
- 'Download CSV' button on player list
- Hitting it downloads \`players.csv\` with columns: name, position, team, date_joined, salary, contact_person
- Works whether search is active or not

**Touches:** new view in \`players/views.py\`, new URL, link in template" \
"story,P2"

create_issue "[3 pts] Export injury report as CSV" \
"As a coach, I can export the injury log as CSV for medical staff.

**Acceptance:**
- Button on injury list
- Downloads \`injuries.csv\` with columns: player, injury_type, body_part, severity, date_reported, expected_return, status

**Touches:** new view in \`injuries/views.py\`, URL, link in template" \
"story,P2"

create_issue "[5 pts] Team-level stats summary" \
"As a coach, I can see average overall score per team so I can compare teams at a glance.

**Acceptance:**
- New page \`/analytics/teams/\` lists each team
- For each: average of latest \`PlayerStats.overall_score\` across players on that team
- Count of players per team
- Sorted by average descending

**Touches:** new view in \`analytics/views.py\` joining \`PlayerStats → VolleyPlayer → Team\`" \
"story,P2"

create_issue "[5 pts] Dashboard homepage" \
"As any user, I see a dashboard at / with top-line counts.

**Acceptance:**
- Counts: total players, total teams, active injuries, upcoming events in next 7 days
- 4 glass-card widgets
- Each card links to its list page

**Touches:** new \`volleyhub/volleyhub/views.py\`, update root URL conf, new \`templates/dashboard.html\`" \
"story,P2"

create_issue "[8 pts] Email reminder for events in next 24h" \
"As a member, I get an email 24h before any event on my team's schedule.

**Acceptance:**
- Management command \`python manage.py send_event_reminders\`
- Sends email for each Event happening in next 24h
- Works with console backend in dev; SMTP settings doc'd in README

**Touches:** new \`teams/management/commands/send_event_reminders.py\`, settings update" \
"story,P3"

create_issue "[5 pts] Unit tests: VolleyPlayer model + player views" \
"Write tests for the Players app.

**Acceptance:**
- Model tests: creation, string repr, default values
- View tests: list, detail, add, edit, delete (smoke tests for 200/302 status codes)
- \`python manage.py test players\` passes

**Touches:** \`players/tests.py\` (currently empty stub)" \
"story,P2"

create_issue "[5 pts] Unit tests: Injury model + recovery % logic" \
"Write tests for the Injuries app.

**Acceptance:**
- Model tests for Injury creation, status transitions
- Test the recovery % progress calculation used in detail view
- \`python manage.py test injuries\` passes

**Touches:** \`injuries/tests.py\`" \
"story,P2"

create_issue "[3 pts] Unit tests: PlayerStats.overall_score property" \
"Write tests for the Analytics app.

**Acceptance:**
- Test \`PlayerStats.overall_score\` returns avg of the 6 metrics
- Boundary tests (all 0s, all 100s)
- \`python manage.py test analytics\` passes

**Touches:** \`analytics/tests.py\`" \
"story,P2"

create_issue "[13 pts → SPLIT] Coach role: coach sees only own team" \
"🚩 Too large — split before pulling into a sprint. Candidate sub-stories:
- Add \`role\` field to user profile (Admin / Coach)
- Link coach user to a specific Team (FK)
- Queryset filtering: coach views limited to their team's players, events, injuries, stats
- Admin vs coach nav differences" \
"story,P3"

create_issue "[5 pts] REST API endpoint: GET /api/players/" \
"As an integrator, I can fetch the player roster as JSON.

**Acceptance:**
- \`GET /api/players/\` returns JSON list of all players
- Includes: id, name, position, team name, date_joined
- Protected by session auth (or token)

**Touches:** new view/URL. Optional: add \`djangorestframework\` to \`requirements.txt\`" \
"story,P3"

create_issue "[5 pts] Player profile photo upload" \
"As an admin, I can attach a photo to a player's profile.

**Acceptance:**
- \`VolleyPlayer.photo\` ImageField (optional)
- Upload on add/edit form
- Displayed on player detail page
- \`MEDIA_URL\` + \`MEDIA_ROOT\` configured

**Touches:** \`players/models.py\`, form, templates, \`volleyhub/volleyhub/settings.py\`, migration" \
"story,P3"

create_issue "[3 pts] Soft-delete players (is_active flag)" \
"As an admin, I can archive a player instead of hard-deleting so historical stats are preserved.

**Acceptance:**
- \`VolleyPlayer.is_active\` BooleanField default True
- 'Delete' button now sets \`is_active=False\`
- List views filter to \`is_active=True\` by default
- Toggle to show archived players

**Touches:** \`players/models.py\`, \`players/views.py\`, migration" \
"story,P3"

create_issue "[8 pts] Event attendance tracking" \
"As a coach, I can mark which players attended a given event.

**Acceptance:**
- New \`Attendance\` model: FK Event, FK VolleyPlayer, Boolean attended, timestamp
- On event detail page: list of team players with check-in toggles
- Save button persists attendance
- Attendance history visible on player detail

**Touches:** new model + migration, event detail view/template, player detail view" \
"story,P3"

echo ""
echo "==> Done. View your backlog:"
echo "   gh issue list --limit 25"
