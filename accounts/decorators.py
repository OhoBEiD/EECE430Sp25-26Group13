"""View decorators that enforce role + ownership rules.

`role_required` gates by `UserProfile.role`. `team_coach_required` gates
by team ownership (the team's coach OR a manager/admin). `self_player_or_role`
lets a player access their own player_pk URL while keeping it open to
listed roles.

All decorators redirect anonymous users to LOGIN_URL via @login_required
and raise `PermissionDenied` (handled by templates/403.html) on a role
mismatch.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .permissions import can_edit_team
from .roles import Role, role_of


def role_required(*roles):
    if not roles:
        raise ValueError('role_required needs at least one role')

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if role_of(request.user) not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def manager_or_admin_required(view):
    return role_required(Role.MANAGER, Role.ADMIN)(view)


def team_coach_required(team_pk_kwarg='pk'):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            from teams.models import Team
            team = get_object_or_404(Team, pk=kwargs[team_pk_kwarg])
            if not can_edit_team(request.user, team):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def self_player_or_role(*allowed_roles, player_pk_kwarg='pk'):
    if not allowed_roles:
        raise ValueError('self_player_or_role needs at least one fallback role')

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            role = role_of(request.user)
            if role in allowed_roles:
                return view(request, *args, **kwargs)
            if role == Role.PLAYER:
                profile = getattr(request.user, 'profile', None)
                target_pk = int(kwargs[player_pk_kwarg])
                if profile and profile.linked_player_id == target_pk:
                    return view(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator
