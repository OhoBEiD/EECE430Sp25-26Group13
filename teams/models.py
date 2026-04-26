from django.conf import settings
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=20, choices=[
        ('U14', 'Under 14'),
        ('U16', 'Under 16'),
        ('U18', 'Under 18'),
        ('Senior', 'Senior'),
    ])
    coach_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Legacy free-text coach label. Prefer the coach FK; this field is dropped in PR 8.',
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coached_teams',
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.age_group})"


class Event(models.Model):
    EVENT_TYPES = [
        ('Practice', 'Practice'),
        ('Game', 'Game'),
        ('Tournament', 'Tournament'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.date}"
