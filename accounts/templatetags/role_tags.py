"""Template tags for role-aware rendering.

Most role checks ride on the booleans injected by `role_context`
(`{% if is_coach %}`). These tags cover the cases that need an object
(can the current user edit *this* team?) or transform a value
(`{% redact_pii %}`).
"""

from django import template

from accounts import permissions
from accounts.roles import VISITOR, Role, role_of

register = template.Library()


def _user_from_context(context):
    request = context.get('request')
    if request is None:
        return None
    return request.user


@register.simple_tag(takes_context=True)
def can_edit_team(context, team):
    user = _user_from_context(context)
    return permissions.can_edit_team(user, team) if user else False


@register.simple_tag(takes_context=True)
def can_edit_player(context, player):
    user = _user_from_context(context)
    return permissions.can_edit_player(user, player) if user else False


@register.simple_tag(takes_context=True)
def can_view_injury(context, injury):
    user = _user_from_context(context)
    return permissions.can_view_injury(user, injury) if user else False


@register.simple_tag(takes_context=True)
def redact_pii(context, value, placeholder='—'):
    """Return value, or `placeholder` for visitors and scouts."""
    user = _user_from_context(context)
    role = role_of(user)
    if role in (VISITOR, Role.SCOUT):
        return placeholder
    return value
