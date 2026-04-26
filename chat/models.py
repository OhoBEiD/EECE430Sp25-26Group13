from django.db import models
from django.conf import settings

class ChatThread(models.Model):
    TYPE_CHOICES = [
        ('team_general', 'Team General'),
        ('team_staff', 'Team Staff'),
        ('event', 'Event Discussion'),
    ]
    name = models.CharField(max_length=255)
    thread_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey('teams.Event', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.get_thread_type_display()}: {self.name}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} - {self.text[:20]}"
