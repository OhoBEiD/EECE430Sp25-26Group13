from django.db import models
from django.db.models import CASCADE, CharField, ForeignKey
from django.core.exceptions import ValidationError

class LineupSlot(models.Model):
    POSITION_CHOICES = [
        ('SETTER', 'Setter'),
        ('OH1',    'Outside Hitter 1'),
        ('OH2',    'Outside Hitter 2'),
        ('MB1',    'Middle Blocker 1'),
        ('MB2',    'Middle Blocker 2'),
        ('OPP',    'Opposite'),
        ('LIBERO', 'Libero'),
    ]
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='lineup_slots')
    position = CharField(max_length=10, choices=POSITION_CHOICES)
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='lineup_slots')

    class Meta:
        unique_together = [('event', 'position'), ('event', 'player')]

    def clean(self):
        if self.event.event_type not in ('Game', 'Tournament'):
            raise ValidationError('Lineups are only for Game or Tournament events.')
        if self.player and self.event and self.player.team_id != self.event.team_id:
            raise ValidationError("Player must be on the event's team.")

    def __str__(self):
        return f"{self.position} - {self.player.name} ({self.event.title})"
