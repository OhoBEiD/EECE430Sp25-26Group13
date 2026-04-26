"""Pure-Python predicates for role-based access checks.
from django.utils import timezone
from datetime import timedelta

Used by views (in conditionals), decorators (in dispatch), querysets
(in filters), and template tags (in `{% can_edit_* %}`). Always safe
for `AnonymousUser`.
"""

from .roles import Role, role_of


def _coach_owns_team(user, team):
    return team is not None and team.coach_id == user.id


def _coach_owns_player(user, player):
    return (
        player is not None
        and player.team_id is not None
        and user.coached_teams.filter(pk=player.team_id).exists()
    )


def _is_self_player(user, player):
    profile = getattr(user, 'profile', None)
    return (
        profile is not None
        and profile.linked_player_id is not None
        and profile.linked_player_id == player.id
    )


def can_edit_team(user, team):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        return _coach_owns_team(user, team)
    return False


def can_edit_player(user, player):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        return _coach_owns_player(user, player)
    return False


def can_record_stats(user, player):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        return _coach_owns_player(user, player)
    return False


def can_view_injury(user, injury):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.SCOUT, Role.ADMIN):
        return True
    if role == Role.COACH:
        return _coach_owns_player(user, injury.player)
    if role == Role.PLAYER:
        return _is_self_player(user, injury.player)
    return False


def can_view_feedback(user, feedback):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        return feedback.coach_id == user.id or _coach_owns_player(user, feedback.player)
    if role == Role.PLAYER:
        return _is_self_player(user, feedback.player)
    return False

def can_edit_feedback(user, feedback):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        if feedback.coach_id == user.id:
            now = timezone.now()
            if now <= feedback.created_at + timedelta(hours=24):
                return True
    return False

def can_delete_feedback(user, feedback):
    if not user.is_authenticated:
        return False
    role = role_of(user)
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    if role == Role.COACH:
        return feedback.coach_id == user.id
    return False
