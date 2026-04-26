from django.db import models


class Role(models.TextChoices):
    PLAYER = 'player', 'Player'
    COACH = 'coach', 'Coach'
    MANAGER = 'manager', 'Manager'
    SCOUT = 'scout', 'Scout'
    ADMIN = 'admin', 'Admin'


VISITOR = 'visitor'


def role_of(user):
    if user is None or not user.is_authenticated:
        return VISITOR
    profile = getattr(user, 'profile', None)
    if profile is None:
        return Role.ADMIN if user.is_superuser else Role.PLAYER
    return profile.role


def is_visitor(user):
    return role_of(user) == VISITOR


def is_player(user):
    return role_of(user) == Role.PLAYER


def is_coach(user):
    return role_of(user) == Role.COACH


def is_manager(user):
    return role_of(user) == Role.MANAGER


def is_scout(user):
    return role_of(user) == Role.SCOUT


def is_admin(user):
    return role_of(user) == Role.ADMIN
