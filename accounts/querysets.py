"""Role-aware querysets.

Each helper returns the queryset the given user is permitted to see.
Visitors get the public read surface (players, teams, stats — but no
injuries). Players are scoped to their own team / own data. Coaches are
scoped to their coached teams. Manager / scout / admin see everything.
"""

from .roles import Role, role_of


def _own_team_id(user):
    profile = getattr(user, 'profile', None)
    if profile is None or profile.linked_player is None:
        return None
    return profile.linked_player.team_id


def _coached_team_ids(user):
    if not user.is_authenticated:
        return []
    return list(user.coached_teams.values_list('id', flat=True))


def players_for(user):
    from players.models import VolleyPlayer

    role = role_of(user)
    if role == Role.PLAYER:
        team_id = _own_team_id(user)
        if team_id is None:
            return VolleyPlayer.objects.none()
        return VolleyPlayer.objects.filter(team_id=team_id)
    if role == Role.COACH:
        team_ids = _coached_team_ids(user)
        if not team_ids:
            return VolleyPlayer.objects.none()
        return VolleyPlayer.objects.filter(team_id__in=team_ids)
    return VolleyPlayer.objects.all()


def teams_for(user):
    from teams.models import Team

    role = role_of(user)
    if role == Role.PLAYER:
        team_id = _own_team_id(user)
        if team_id is None:
            return Team.objects.none()
        return Team.objects.filter(pk=team_id)
    if role == Role.COACH:
        team_ids = _coached_team_ids(user)
        if not team_ids:
            return Team.objects.none()
        return Team.objects.filter(pk__in=team_ids)
    return Team.objects.all()


def injuries_for(user):
    from injuries.models import Injury

    role = role_of(user)
    if not user.is_authenticated:
        return Injury.objects.none()
    if role == Role.PLAYER:
        profile = getattr(user, 'profile', None)
        if profile is None or profile.linked_player_id is None:
            return Injury.objects.none()
        return Injury.objects.filter(player_id=profile.linked_player_id)
    if role == Role.COACH:
        team_ids = _coached_team_ids(user)
        if not team_ids:
            return Injury.objects.none()
        return Injury.objects.filter(player__team_id__in=team_ids)
    return Injury.objects.all()


def stats_for(user):
    from analytics.models import PlayerStats

    role = role_of(user)
    if role == Role.PLAYER:
        profile = getattr(user, 'profile', None)
        if profile is None or profile.linked_player_id is None:
            return PlayerStats.objects.none()
        return PlayerStats.objects.filter(player_id=profile.linked_player_id)
    if role == Role.COACH:
        team_ids = _coached_team_ids(user)
        if not team_ids:
            return PlayerStats.objects.none()
        return PlayerStats.objects.filter(player__team_id__in=team_ids)
    return PlayerStats.objects.all()
