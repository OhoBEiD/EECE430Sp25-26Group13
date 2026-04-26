from django.db import models
from django.db.models import CASCADE, SET_NULL, Index, TextField, ForeignKey, DateTimeField
from django.conf import settings

class Feedback(models.Model):
    event = ForeignKey('teams.Event', on_delete=CASCADE, related_name='feedback')
    player = ForeignKey('players.VolleyPlayer', on_delete=CASCADE, related_name='feedback')
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, related_name='feedback_written')
    body = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [Index(fields=['player', '-created_at'])]

    def __str__(self):
        return f"Feedback for {self.player.name} on {self.event.title}"
