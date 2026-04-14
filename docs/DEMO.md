# Lab Demo Cheat-Sheet — VolleyHub

**Duration target: 7–10 minutes.** Instructor wants a user-facing demo, not a code walkthrough. Focus on "what have you built that matches requirements" + "time vs. velocity" story.

---

## 5-minute pre-demo setup

1. Open a terminal in the repo:
   ```bash
   cd "/Users/omarobeid/volleyball club/volleyhub"
   source ../my_venv/bin/activate
   python manage.py migrate
   python manage.py seed_demo        # wipes + seeds fresh demo data
   python manage.py createsuperuser  # first time only — for admin demo
   python manage.py runserver
   ```
2. Open **three browser tabs**, resize them side-by-side:
   - **Tab 1:** http://localhost:8000/ (the app)
   - **Tab 2:** https://github.com/OhoBEiD/EECE430Sp25-26Group13 (the repo)
   - **Tab 3:** https://github.com/users/OhoBEiD/projects/2 (the Project board)
3. Make sure you're **logged out** in Tab 1 before starting.

## Demo accounts

| User | Password | Role (narrative) |
|------|----------|------------------|
| `manager_sara` | `demo12345` | Club Manager — full CRUD |
| `coach_ahmad` | `demo12345` | Team Coach — records stats, logs injuries |
| `scout_layla` | `demo12345` | Scout — read/write player data |
| _superuser_ (your own) | _your pw_ | Django admin access |

(Role-based permissions aren't enforced yet — that's story #16 in the backlog. In the demo we use the different named accounts to tell a story; the underlying auth is the same.)

---

## The demo — hit these beats in order

### Beat 1 — The repo and Scrum trail (1 min)

**Switch to Tab 2 (GitHub repo).**

> "This is our repo. 3-person team, every change went through a pull request, squashed into main."

- Scroll the commit history on `main`. Point out the feature-branch merge pattern and the issue references in commit messages.
- Click **Pull requests → Closed** → 7+ merged PRs visible.
- Click the **Tags** page (or `/releases`) — show **v0.1-sprint1** and **v0.2-sprint2** — "Two shippable increments, tagged."

### Beat 2 — The backlog and velocity (1.5 min)

**Switch to Tab 3 (Project board).**

> "20-story product backlog, sized in points via planning poker. Sprint 1 was the calibration sprint — planned 10, hit 10. Sprint 2 we stretched to 11, hit 11."

- Show columns: **Product Backlog / Sprint Backlog / In Progress / In Review / Done**.
- Filter by Sprint → Sprint 1 — 4 cards in Done (auth #1, protect CRUD #2, search #3, paginate #6).
- Filter by Sprint → Sprint 2 — 3 cards in Done (filter injuries #4, CSV export #8, dashboard #11).
- Open `docs/sprint1-retro.md` and `docs/sprint2-retro.md` briefly — "We wrote retros after each sprint."

### Beat 3 — Dashboard as a visitor (30 s)

**Switch to Tab 1 → http://localhost:8000/ (logged out).**

> "Visitor lands on the dashboard — club snapshot. Anything in red is an active injury, amber is upcoming events."

- Point at the 4 stat cards (players / teams / active injuries / events next 7 days).
- Scroll to upcoming-events list.
- Click an **Active Injuries** card → injury list opens in Active filter. "Read-only for the public."

### Beat 4 — Public browsing, gated editing (30 s)

> "Public can see rosters but can't edit."

- Click **Players** icon in the dock → roster renders.
- Click any player's **Edit** button → redirects to `/accounts/login/?next=…`. "That's `@login_required` kicking in."

### Beat 5 — Log in as the Manager (1.5 min)

**Login as `manager_sara` / `demo12345`.**

> "Now I'm the club manager. I can actually add players."

- Dashboard shows a welcome message.
- Click **Players** → use the **search box** to filter by "Omar" → shows Omar Tannous. "That's Sprint 1 story #3."
- Click **Clear** → back to full list. Scroll to show pagination ("Page 1 of 2"). Click **Next** → page 2 loads instantly with no re-animation of the header. "Sprint 1 story #6."
- Click **Download CSV** → browser downloads `players.csv`. Open it — show the roster export. "Sprint 2 story #8."

### Beat 6 — Coach view: injuries + events (1.5 min)

**Log out → log in as `coach_ahmad` / `demo12345`.**

> "As the coach, my focus is on injuries and the schedule."

- Click **Injuries** icon in dock → injury list.
- Click the **Active** pill tab → 2 active cases shown (Hassan, Lea). "Sprint 2 story #4 — filter by status."
- Click **Log New Injury** → form renders (styled glassmorphism). Cancel out.
- Click **Teams** icon → pick "Beirut Blazers" → team detail with events.
- Back on Teams page, click **Schedule** (the button that was invisible before — now fixed in a bugfix PR). Shows 6 events across 3 teams grouped by date.

### Beat 7 — Analytics for stat-tracking (1 min)

> "We also track performance. Coach picks a player and logs game stats."

- Click **Analytics** in the dock.
- Click **Omar Tannous** → dashboard with overall score trend + 6 metric breakdown over 3 weeks.
- Point at the metric cards: serve accuracy rising, spike success improving. "The seed created 3 weeks of progress data."

### Beat 8 — The Scrum story close (1 min)

**Back to Tab 3 (board) or tab 2 (retros).**

> "Summary. We ran two sprints. We honestly measured our velocity — 10 and 11 points — and completed 100% of committed scope both times. Two shippable tags on main. Remaining 13 backlog items are sized and ready for future sprints."

If there's time:
- Show the commit graph or PR list again.
- Mention the role-based access (#16) as explicit future work ("coach/manager/scout permissions is a 13-pointer still in the backlog").

---

## Quick talking points (if asked)

- **"Why Django?"** Built-in auth, admin, ORM — unblocked us fast for a 2-sprint timeline.
- **"Why self-merged PRs?"** Teammates weren't added as collaborators until late. Flagged in retros; branch protection is on the to-do list.
- **"Why so many UI polish commits on main?"** Small UX bugs (invisible buttons, replaying animations) we found between sprints — shipped as bugfixes, kept sprint point counts honest.
- **"How did you plan the backlog?"** 20 user stories derived from a gap analysis of the existing codebase. Each was a real missing feature (auth, filtering, pagination, CSV export, dashboard, tests, etc.). Stories were sized using Fibonacci points via planning poker.

---

## If something breaks live

- **Server 500?** Ctrl+C → `python manage.py migrate` → restart. If that fails, run `python manage.py seed_demo` to reset data.
- **Can't log in?** The superuser and demo users all exist if seed was run. Password for demo users is always `demo12345`.
- **Server port in use?** Use `python manage.py runserver 8001`.

---

## What's on the instructor's checklist (from email)

- [x] App prepared — can demo without setup time
- [x] On time — planned 8-minute flow, stop at 10
- [x] "Just a demo, no reports" — no separate deliverable needed
- [x] User personas — manager, coach, scout accounts seeded
- [x] Code matches requirements — walk through each Sprint story live
- [x] Time vs. velocity — retro docs + board + tags tell this story
- [x] Lab recording — be on camera the whole time
