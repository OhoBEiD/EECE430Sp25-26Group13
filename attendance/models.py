from django.conf import settings
from django.db import models
from django.db.models import CASCADE, SET_NULL, Index, CharField, TextField, ForeignKey, DateTimeField

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='attendance')
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='attendance')
    status = CharField(max_length=10, choices=STATUS_CHOICES)
    notes = TextField(blank=True)
    marked_by = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True)
    marked_at = DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('event', 'player')]
        indexes = [Index(fields=['player', 'status'])]

    def __str__(self):
        return f"{self.player.name} - {self.event.title} ({self.status})"

class EventRSVP(models.Model):
    STATUS_CHOICES = [
        ('attending', 'Attending'),
        ('not_attending', 'Not Attending'),
        ('maybe', 'Maybe'),
    ]
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='rsvps')
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='rsvps')
    status = CharField(max_length=20, choices=STATUS_CHOICES)
    reason = TextField(blank=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('event', 'player')]

    def __str__(self):
        return f"{self.player.name} RSVP for {self.event.title} ({self.status})"
