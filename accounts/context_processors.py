"""Inject role flags into every template's context.

Templates can read `is_coach`, `is_manager`, `linked_player`, etc., and
do `{% if is_coach or is_manager %}…{% endif %}` without importing
anything. The boolean shape keeps templates dumb — all role logic
lives in Python.
"""

from .roles import VISITOR, Role, role_of


def role_context(request):
    user = request.user
    role = role_of(user)
    profile = getattr(user, 'profile', None) if user.is_authenticated else None
    if user.is_authenticated and hasattr(user, 'coached_teams'):
        coached_teams = user.coached_teams.all()
    else:
        coached_teams = []

    return {
        'user_role': role,
        'linked_player': profile.linked_player if profile else None,
        'coached_teams': coached_teams,
        'is_visitor': role == VISITOR,
        'is_player': role == Role.PLAYER,
        'is_coach': role == Role.COACH,
        'is_manager': role == Role.MANAGER,
        'is_scout': role == Role.SCOUT,
        'is_admin': role == Role.ADMIN,
    }
