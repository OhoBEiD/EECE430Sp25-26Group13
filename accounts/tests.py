"""Unit tests for the role infrastructure: decorators, permissions, querysets, template tags.

Each test seeds a minimal world (one team, one player, one user per role)
so a regression in one helper fails its own focused test instead of
bringing the whole sprint-3 layer down at once.
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from analytics.models import PlayerStats
from injuries.models import Injury
from players.models import VolleyPlayer
from teams.models import Team

from .decorators import (
    role_required,
    self_player_or_role,
    team_coach_required,
)
from .permissions import (
    can_edit_player,
    can_edit_team,
    can_record_stats,
    can_view_injury,
)
from .querysets import injuries_for, players_for, stats_for, teams_for
from .roles import VISITOR, Role, role_of


class RoleWorld:
    """Minimal world: 2 teams, 2 players, one user per role."""

    def __init__(self):
        self.team_blazers = Team.objects.create(name='Blazers', age_group='Senior', coach_name='—')
        self.team_cedars = Team.objects.create(name='Cedars', age_group='U18', coach_name='—')

        self.player_omar = VolleyPlayer.objects.create(
            name='Omar', date_joined=date.today(), position='Setter',
            salary=Decimal('1000'), contact_person='—', team=self.team_blazers,
        )
        self.player_outsider = VolleyPlayer.objects.create(
            name='Stranger', date_joined=date.today(), position='Libero',
            salary=Decimal('900'), contact_person='—', team=self.team_cedars,
        )

        self.u_player = self._user('p', Role.PLAYER, linked_player=self.player_omar)
        self.u_coach = self._user('c', Role.COACH)
        self.u_manager = self._user('m', Role.MANAGER)
        self.u_scout = self._user('s', Role.SCOUT)
        self.u_admin = self._user('a', Role.ADMIN)

        self.team_blazers.coach = self.u_coach
        self.team_blazers.save()

        self.injury_omar = Injury.objects.create(
            player=self.player_omar, injury_type='Sprain', body_part='Ankle',
            severity='Low', date_reported=date.today(), status='Active',
            reported_by='—',
        )
        self.injury_outsider = Injury.objects.create(
            player=self.player_outsider, injury_type='Bruise', body_part='Knee',
            severity='Low', date_reported=date.today(), status='Active',
            reported_by='—',
        )
        self.stats_omar = PlayerStats.objects.create(
            player=self.player_omar, date_recorded=date.today(),
            serve_accuracy=70, spike_success=70, block_rate=70,
            dig_success=70, set_accuracy=70, receive_rating=70,
        )

    @staticmethod
    def _user(prefix, role, linked_player=None):
        is_super = role == Role.ADMIN
        u = (User.objects.create_superuser if is_super else User.objects.create_user)(
            username=f'{prefix}_{role}', password='x',
            **({'email': f'{prefix}@x.test'} if is_super else {}),
        )
        u.profile.role = role
        u.profile.linked_player = linked_player
        u.profile.save()
        return u


class RoleHelperTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()

    def test_role_of_anonymous_is_visitor(self):
        self.assertEqual(role_of(AnonymousUser()), VISITOR)

    def test_role_of_returns_profile_role(self):
        self.assertEqual(role_of(self.world.u_coach), Role.COACH)
        self.assertEqual(role_of(self.world.u_manager), Role.MANAGER)


class PermissionPredicateTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()

    def test_can_edit_team(self):
        w = self.world
        self.assertFalse(can_edit_team(AnonymousUser(), w.team_blazers))
        self.assertFalse(can_edit_team(w.u_player, w.team_blazers))
        self.assertFalse(can_edit_team(w.u_scout, w.team_blazers))
        self.assertTrue(can_edit_team(w.u_coach, w.team_blazers))
        self.assertFalse(can_edit_team(w.u_coach, w.team_cedars))
        self.assertTrue(can_edit_team(w.u_manager, w.team_cedars))
        self.assertTrue(can_edit_team(w.u_admin, w.team_cedars))

    def test_can_edit_player(self):
        w = self.world
        self.assertTrue(can_edit_player(w.u_coach, w.player_omar))
        self.assertFalse(can_edit_player(w.u_coach, w.player_outsider))
        self.assertTrue(can_edit_player(w.u_manager, w.player_outsider))
        self.assertFalse(can_edit_player(w.u_player, w.player_omar))

    def test_can_record_stats_mirrors_edit_player(self):
        w = self.world
        self.assertTrue(can_record_stats(w.u_coach, w.player_omar))
        self.assertFalse(can_record_stats(w.u_coach, w.player_outsider))
        self.assertFalse(can_record_stats(w.u_scout, w.player_omar))

    def test_can_view_injury(self):
        w = self.world
        self.assertTrue(can_view_injury(w.u_player, w.injury_omar))
        self.assertFalse(can_view_injury(w.u_player, w.injury_outsider))
        self.assertTrue(can_view_injury(w.u_coach, w.injury_omar))
        self.assertFalse(can_view_injury(w.u_coach, w.injury_outsider))
        self.assertTrue(can_view_injury(w.u_scout, w.injury_outsider))
        self.assertTrue(can_view_injury(w.u_manager, w.injury_outsider))


class QuerysetScopingTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()

    def test_players_scoped_per_role(self):
        w = self.world
        self.assertEqual(set(players_for(AnonymousUser())), {w.player_omar, w.player_outsider})
        self.assertEqual(set(players_for(w.u_player)), {w.player_omar})
        self.assertEqual(set(players_for(w.u_coach)), {w.player_omar})
        self.assertEqual(set(players_for(w.u_manager)), {w.player_omar, w.player_outsider})

    def test_teams_scoped_per_role(self):
        w = self.world
        self.assertEqual(set(teams_for(w.u_player)), {w.team_blazers})
        self.assertEqual(set(teams_for(w.u_coach)), {w.team_blazers})
        self.assertEqual(set(teams_for(w.u_scout)), {w.team_blazers, w.team_cedars})

    def test_injuries_scoped_per_role(self):
        w = self.world
        self.assertEqual(set(injuries_for(AnonymousUser())), set())
        self.assertEqual(set(injuries_for(w.u_player)), {w.injury_omar})
        self.assertEqual(set(injuries_for(w.u_coach)), {w.injury_omar})
        self.assertEqual(set(injuries_for(w.u_scout)), {w.injury_omar, w.injury_outsider})

    def test_stats_scoped_per_role(self):
        w = self.world
        self.assertEqual(set(stats_for(w.u_player)), {w.stats_omar})
        self.assertEqual(set(stats_for(w.u_manager)), {w.stats_omar})


class DecoratorTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()
        self.factory = RequestFactory()

    @staticmethod
    def _ok_view(request, *args, **kwargs):
        return HttpResponse('ok')

    def _request(self, user):
        request = self.factory.get('/x/')
        request.user = user
        return request

    def test_role_required_allows_listed_role(self):
        view = role_required(Role.MANAGER)(self._ok_view)
        response = view(self._request(self.world.u_manager))
        self.assertEqual(response.status_code, 200)

    def test_role_required_blocks_other_roles(self):
        view = role_required(Role.MANAGER)(self._ok_view)
        with self.assertRaises(PermissionDenied):
            view(self._request(self.world.u_player))

    def test_role_required_redirects_anonymous(self):
        view = role_required(Role.MANAGER)(self._ok_view)
        response = view(self._request(AnonymousUser()))
        self.assertEqual(response.status_code, 302)

    def test_team_coach_required_allows_assigned_coach(self):
        view = team_coach_required('team_pk')(self._ok_view)
        response = view(self._request(self.world.u_coach), team_pk=self.world.team_blazers.pk)
        self.assertEqual(response.status_code, 200)

    def test_team_coach_required_blocks_other_coach(self):
        view = team_coach_required('team_pk')(self._ok_view)
        with self.assertRaises(PermissionDenied):
            view(self._request(self.world.u_coach), team_pk=self.world.team_cedars.pk)

    def test_team_coach_required_allows_manager(self):
        view = team_coach_required('team_pk')(self._ok_view)
        response = view(self._request(self.world.u_manager), team_pk=self.world.team_cedars.pk)
        self.assertEqual(response.status_code, 200)

    def test_self_player_or_role_allows_own_pk(self):
        view = self_player_or_role(Role.MANAGER, player_pk_kwarg='player_pk')(self._ok_view)
        response = view(self._request(self.world.u_player), player_pk=self.world.player_omar.pk)
        self.assertEqual(response.status_code, 200)

    def test_self_player_or_role_blocks_other_player(self):
        view = self_player_or_role(Role.MANAGER, player_pk_kwarg='player_pk')(self._ok_view)
        with self.assertRaises(PermissionDenied):
            view(self._request(self.world.u_player), player_pk=self.world.player_outsider.pk)

    def test_self_player_or_role_allows_listed_role(self):
        view = self_player_or_role(Role.SCOUT, player_pk_kwarg='player_pk')(self._ok_view)
        response = view(self._request(self.world.u_scout), player_pk=self.world.player_outsider.pk)
        self.assertEqual(response.status_code, 200)


class TemplateTagTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()
        self.factory = RequestFactory()

    def _render(self, template_str, user, **extra):
        request = self.factory.get('/x/')
        request.user = user
        ctx = Context({'request': request, 'user': user, **extra})
        return Template('{% load role_tags %}' + template_str).render(ctx).strip()

    def test_can_edit_team_tag(self):
        rendered = self._render(
            '{% can_edit_team team as ok %}{{ ok }}',
            self.world.u_coach, team=self.world.team_blazers,
        )
        self.assertEqual(rendered, 'True')

    def test_redact_pii_blanks_for_scout(self):
        rendered = self._render(
            '{% redact_pii "secret" %}', self.world.u_scout,
        )
        self.assertEqual(rendered, '—')

    def test_redact_pii_passes_through_for_manager(self):
        rendered = self._render(
            '{% redact_pii "secret" %}', self.world.u_manager,
        )
        self.assertEqual(rendered, 'secret')

    def test_redact_pii_blanks_for_visitor(self):
        rendered = self._render(
            '{% redact_pii "secret" %}', AnonymousUser(),
        )
        self.assertEqual(rendered, '—')


class ContextProcessorTests(TestCase):
    def setUp(self):
        self.world = RoleWorld()
        self.factory = RequestFactory()

    def _ctx(self, user):
        from .context_processors import role_context
        request = self.factory.get('/x/')
        request.user = user
        return role_context(request)

    def test_anonymous_is_visitor(self):
        ctx = self._ctx(AnonymousUser())
        self.assertTrue(ctx['is_visitor'])
        self.assertEqual(ctx['user_role'], VISITOR)
        self.assertIsNone(ctx['linked_player'])

    def test_player_exposes_linked_player(self):
        ctx = self._ctx(self.world.u_player)
        self.assertTrue(ctx['is_player'])
        self.assertEqual(ctx['linked_player'], self.world.player_omar)

    def test_coach_exposes_coached_teams(self):
        ctx = self._ctx(self.world.u_coach)
        self.assertTrue(ctx['is_coach'])
        self.assertEqual(list(ctx['coached_teams']), [self.world.team_blazers])
