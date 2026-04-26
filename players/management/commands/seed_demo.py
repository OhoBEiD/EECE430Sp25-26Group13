"""
Seed the VolleyHub database with realistic demo data for the lab demo.

Creates:
- 6 user accounts across all roles (visitor is implicit / not seeded):
    player_omar, coach_ahmad, manager_sara, scout_layla, admin_volleyhub
    All passwords are `demo12345`.
- 3 teams across different age groups
- 15 players distributed across the teams (player_omar is linked to players[0])
- 6 events (past, today, next few days, next week)
- 4 injuries (2 active, 1 recovering, 1 cleared)
- 3 sets of player stats per team captain

Idempotent — safe to run multiple times. Wipes demo-owned records first.

Usage:
    python manage.py seed_demo
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from players.models import VolleyPlayer
from teams.models import Team, Event
from injuries.models import Injury
from analytics.models import PlayerStats
from accounts.models import UserProfile
from accounts.roles import Role


# (username, first, last, email, role)
DEMO_USERS = [
    ('player_omar',     'Omar',  'Tannous',  'omar@volleyhub.demo',    Role.PLAYER),
    ('coach_ahmad',     'Ahmad', 'Khoury',   'coach@volleyhub.demo',   Role.COACH),
    ('manager_sara',    'Sara',  'Mansour',  'manager@volleyhub.demo', Role.MANAGER),
    ('scout_layla',     'Layla', 'Haddad',   'scout@volleyhub.demo',   Role.SCOUT),
    ('admin_volleyhub', 'Admin', 'VolleyHub', 'admin@volleyhub.demo',  Role.ADMIN),
]
DEMO_PASSWORD = 'demo12345'

DEMO_TEAMS = [
    {'name': 'Beirut Blazers', 'age_group': 'Senior', 'coach_name': 'Coach Ahmad Khoury',
     'description': 'Senior men\'s competitive squad — 2025 regional finalists.'},
    {'name': 'Cedars U18', 'age_group': 'U18', 'coach_name': 'Coach Nour Saleh',
     'description': 'Youth development program feeding the senior roster.'},
    {'name': 'Phoenix Rising', 'age_group': 'U16', 'coach_name': 'Coach Rami Youssef',
     'description': 'Under-16 girls\' team; focus on fundamentals and teamwork.'},
]

POSITIONS = ['Setter', 'Outside Hitter', 'Middle Blocker', 'Opposite Hitter', 'Libero', 'Defensive Specialist']

DEMO_PLAYERS = [
    # Beirut Blazers (Senior)
    ('Omar Tannous', 'Setter', 2500, '03 111 222'),
    ('Hassan Abou Chacra', 'Outside Hitter', 2800, '03 333 444'),
    ('Elie Farah', 'Middle Blocker', 2400, '03 555 666'),
    ('Ziad Karam', 'Libero', 2200, '03 777 888'),
    ('Karim Nasr', 'Opposite Hitter', 2600, '03 999 000'),
    # Cedars U18
    ('Rami Hajj', 'Setter', 1200, '71 111 222'),
    ('Tarek Boulos', 'Middle Blocker', 1100, '71 333 444'),
    ('Joseph Maalouf', 'Outside Hitter', 1300, '71 555 666'),
    ('Ali Bassil', 'Libero', 900, '71 777 888'),
    ('Charbel Azar', 'Defensive Specialist', 1000, '71 999 000'),
    # Phoenix Rising (U16)
    ('Yasmine Khalil', 'Setter', 800, '76 111 222'),
    ('Lea Deeb', 'Outside Hitter', 900, '76 333 444'),
    ('Maya Ghanem', 'Middle Blocker', 850, '76 555 666'),
    ('Nour Abdallah', 'Libero', 700, '76 777 888'),
    ('Rita Chehade', 'Opposite Hitter', 900, '76 999 000'),
]


class Command(BaseCommand):
    help = 'Seed the DB with demo data for the lab presentation.'

    @transaction.atomic
    def handle(self, *args, **options):
        today = date.today()

        self.stdout.write('→ Wiping prior demo data…')
        PlayerStats.objects.all().delete()
        Injury.objects.all().delete()
        Event.objects.all().delete()
        VolleyPlayer.objects.all().delete()
        Team.objects.all().delete()
        User.objects.filter(username__in=[u[0] for u in DEMO_USERS]).delete()

        self.stdout.write('→ Creating demo users…')
        users_by_name = {}
        for username, first, last, email, role in DEMO_USERS:
            is_admin = role == Role.ADMIN
            if is_admin:
                u = User.objects.create_superuser(
                    username=username, email=email, password=DEMO_PASSWORD,
                    first_name=first, last_name=last,
                )
            else:
                u = User.objects.create_user(
                    username=username, email=email,
                    first_name=first, last_name=last,
                    password=DEMO_PASSWORD,
                )
            UserProfile.objects.update_or_create(
                user=u, defaults={'role': role},
            )
            users_by_name[username] = u
            self.stdout.write(f'  • {u.username:20s} role={role:8s} / {DEMO_PASSWORD}')

        self.stdout.write('→ Creating teams…')
        teams = [Team.objects.create(**t) for t in DEMO_TEAMS]

        self.stdout.write('→ Creating players…')
        players = []
        for i, (name, pos, salary, contact) in enumerate(DEMO_PLAYERS):
            team = teams[i // 5]
            p = VolleyPlayer.objects.create(
                name=name,
                date_joined=today - timedelta(days=30 + i * 5),
                position=pos,
                salary=Decimal(salary),
                contact_person=contact,
                team=team,
                photo=f'players/portraits/p{i + 1}.jpg',
            )
            players.append(p)

        self.stdout.write('→ Linking player_omar → Omar Tannous (Beirut Blazers)…')
        omar_profile = users_by_name['player_omar'].profile
        omar_profile.linked_player = players[0]
        omar_profile.save()

        self.stdout.write('→ Creating events…')
        events_spec = [
            (teams[0], 'Strength & conditioning', 'Practice', today - timedelta(days=2), time(18, 0), time(20, 0), 'Main Court', 'Focus on vertical jump.'),
            (teams[0], 'Friendly vs Tripoli Spikers', 'Game',     today + timedelta(days=1), time(19, 0), time(21, 30), 'Beirut Sports Arena', 'Scout Tripoli\'s new setter.'),
            (teams[1], 'Spike drills', 'Practice', today,                           time(17, 0), time(19, 0), 'Training Hall B', ''),
            (teams[1], 'U18 Regional Tournament', 'Tournament', today + timedelta(days=3), time(9,  0), time(17, 0), 'Zahle Stadium', 'Group stage: 3 matches.'),
            (teams[2], 'Receive & dig clinic', 'Practice', today + timedelta(days=2), time(16, 0), time(18, 0), 'Training Hall A', ''),
            (teams[2], 'Phoenix vs Jounieh Juniors', 'Game', today + timedelta(days=6), time(17, 0), time(19, 30), 'Jounieh Club Court', ''),
        ]
        for team, title, ev_type, d, st, et, loc, notes in events_spec:
            Event.objects.create(team=team, title=title, event_type=ev_type,
                                 date=d, start_time=st, end_time=et,
                                 location=loc, notes=notes)

        self.stdout.write('→ Creating injuries…')
        Injury.objects.create(
            player=players[1],  # Hassan
            injury_type='Sprain', body_part='Ankle', severity='Medium',
            date_reported=today - timedelta(days=4),
            expected_return=today + timedelta(days=7),
            status='Active',
            reported_by='Coach Ahmad',
            medical_notes='Rolled left ankle at practice. Mild swelling, RICE protocol.',
        )
        Injury.objects.create(
            player=players[2],  # Elie
            injury_type='Tendinitis', body_part='Knee', severity='Low',
            date_reported=today - timedelta(days=14),
            expected_return=today + timedelta(days=3),
            status='Recovering',
            reported_by='Dr. Haddad',
            medical_notes='Patellar tendinitis. Load management and eccentric work.',
        )
        Injury.objects.create(
            player=players[7],  # Joseph
            injury_type='Bruise', body_part='Shoulder', severity='Low',
            date_reported=today - timedelta(days=25),
            expected_return=today - timedelta(days=10),
            status='Cleared',
            reported_by='Coach Nour',
            medical_notes='Contact bruise during game — fully cleared.',
        )
        Injury.objects.create(
            player=players[11],  # Lea
            injury_type='Strain', body_part='Back', severity='High',
            date_reported=today - timedelta(days=2),
            expected_return=today + timedelta(days=21),
            status='Active',
            reported_by='Coach Rami',
            medical_notes='Lower back strain. MRI scheduled. Out 3 weeks minimum.',
        )

        self.stdout.write('→ Creating player stats…')
        # Record 3 stat lines for one captain per team — so analytics dashboard shows trends
        captains = [players[0], players[5], players[10]]
        for captain in captains:
            for offset, stats in enumerate([
                (68, 65, 60, 72, 80, 70),
                (72, 70, 64, 74, 82, 73),
                (76, 75, 68, 77, 85, 76),
            ]):
                PlayerStats.objects.create(
                    player=captain,
                    date_recorded=today - timedelta(days=(2 - offset) * 7),
                    serve_accuracy=stats[0], spike_success=stats[1],
                    block_rate=stats[2], dig_success=stats[3],
                    set_accuracy=stats[4], receive_rating=stats[5],
                    notes=f'Week {offset + 1} measurement.',
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Seeded. Users: {", ".join(u[0] for u in DEMO_USERS)} (password: {DEMO_PASSWORD})'
        ))
        self.stdout.write(self.style.SUCCESS(
            'Visitor role is implicit — just open the site without signing in.'
        ))
