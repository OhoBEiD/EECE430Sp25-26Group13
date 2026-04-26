# VolleyHub

Django web app to manage a volleyball club: players, teams, events, injuries, and performance analytics.

Built as the EECE430 (Spring 2025–26, Group 13) Scrum assignment.

## Team & Scrum roles

| Member | Role |
|--------|------|
| Omar Obeid (`@OhoBEiD`) | Product Owner + Scrum Master |
| _Teammate 2_ | Developer |
| _Teammate 3_ | Developer |

> **TODO:** fill in teammate names + GitHub handles.

## Project board

Sprint board lives at **Projects → VolleyHub Sprints** in this repo.

Columns: Product Backlog · Sprint Backlog · In Progress · In Review · Done.

## Run locally

```bash
git clone https://github.com/OhoBEiD/EECE430Sp25-26Group13.git volleyhub
cd volleyhub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # first time only
python manage.py runserver
```

Then open http://localhost:8000.

### Run in Docker
```bash
docker build -t volleyhub .
docker run -p 8000:8000 volleyhub
```

## Apps

- `players/` — volleyball player roster (CRUD, positions, team assignment)
- `teams/` — teams by age group + event scheduling (practice/game/tournament)
- `injuries/` — injury tracking with recovery status and expected return
- `analytics/` — per-player performance stats across 6 metrics + trends
- `accounts/` — `UserProfile` (role + linked player), role decorators, per-role dashboards, `/me/`, `/coach/`, `/admin-ui/users/`

## Roles

Six roles, each with a different dashboard, dock, and capability set. Visitor is implicit (anonymous request, no DB row).

| Role | Dashboard | Read scope | Write scope |
|---|---|---|---|
| **Visitor** | `dashboard_visitor` | All players/teams/schedule (PII redacted) | None |
| **Player** | `dashboard_player` | Own team only; own injuries; own stats | None |
| **Coach** | `dashboard_coach` + `/coach/` | Own coached teams + their players/injuries/stats | Edit own team, manage roster, log injuries, record stats |
| **Manager** | `dashboard_manager` | All | Full CRUD + CSV export |
| **Scout** | `dashboard_scout` | All (with `medical_notes`, `salary`, `contact_person` redacted) | None |
| **Admin** | `dashboard_admin` + `/admin-ui/users/` | All | Full CRUD + role assignment + Django admin |

Demo accounts (`demo12345`): `player_omar`, `coach_ahmad`, `manager_sara`, `scout_layla`, `admin_volleyhub`.

Manual verification walk-through: [`docs/sprint3-verification.md`](docs/sprint3-verification.md).

## Definition of Done

A user story is **Done** when:

1. Code is on a feature branch named `feature/issue-<n>-<slug>`.
2. Pull request opened, reviewed by ≥1 teammate.
3. Merged into `main` via **Squash and merge**.
4. App still runs: `python manage.py runserver` with no errors.
5. New behavior manually tested; unit test added if it's a testing story.

## Velocity

| Sprint | Dates | Planned (pts) | Completed (pts) | Tag |
|--------|-------|---------------|-----------------|-----|
| 1 | 2026-04-14 | 10 | 10 | `v0.1-sprint1` |
| 2 | 2026-04-14 | 11 | 11 | `v0.2-sprint2` |
| 3 | 2026-04-26 | 33 | 33 | `v0.3-sprint3` |

Sprint 3 (role-based interfaces) shipped as 8 PRs: foundation → ownership FKs → permission infra → per-role dashboards/dock → players/teams enforcement → injuries/analytics enforcement + PII redaction → dedicated pages (/me, /coach, /admin-ui) → cleanup.

Retros: [`docs/sprint1-retro.md`](docs/sprint1-retro.md) · [`docs/sprint2-retro.md`](docs/sprint2-retro.md)

## Sprint workflow (per story)

```bash
git checkout main && git pull
git checkout -b feature/issue-<n>-<slug>

# ...edit files, test locally with: python manage.py runserver...

git add <files>
git commit -m "feat(<app>): <short description> (#<n>)"
git push -u origin feature/issue-<n>-<slug>
gh pr create --title "<Story title> (#<n>)" --body "Closes #<n>"
```

Teammate reviews → approves → **Squash and merge** on GitHub. Issue auto-closes.
