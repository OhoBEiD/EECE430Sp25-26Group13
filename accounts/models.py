from django.conf import settings
from django.db import models

from .roles import Role


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.PLAYER,
    )
    linked_player = models.ForeignKey(
        'players.VolleyPlayer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        help_text='When role=player, the VolleyPlayer record this account represents.',
    )

    class Meta:
        indexes = [models.Index(fields=['role'])]

    def __str__(self):
        return f'{self.user.username} ({self.role})'
