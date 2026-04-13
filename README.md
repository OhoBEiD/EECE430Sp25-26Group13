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
| 1 | TBD | 10 | TBD | `v0.1-sprint1` |
| 2 | TBD | TBD | TBD | `v0.2-sprint2` |

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
