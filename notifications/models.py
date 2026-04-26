from django.conf import settings
from django.db import models


class Notification(models.Model):
    KIND_EVENT = 'event'
    KIND_RSVP = 'rsvp'
    KIND_GENERIC = 'generic'
    KIND_CHOICES = [
        (KIND_EVENT, 'Event'),
        (KIND_RSVP, 'RSVP'),
        (KIND_GENERIC, 'Notice'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_GENERIC)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'read', '-created_at'])]

    def __str__(self):
        return f'{self.user.username}: {self.title}'
