from django.db import models
from players.models import VolleyPlayer


class Injury(models.Model):
    SEVERITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    STATUS_CHOICES = [('Active', 'Active'), ('Recovering', 'Recovering'), ('Cleared', 'Cleared')]
    INJURY_TYPES = [
        ('Sprain', 'Sprain'), ('Strain', 'Strain'), ('Fracture', 'Fracture'),
        ('Concussion', 'Concussion'), ('Dislocation', 'Dislocation'),
        ('Tendinitis', 'Tendinitis'), ('Bruise', 'Bruise'), ('Other', 'Other'),
    ]
    BODY_PARTS = [
        ('Knee', 'Knee'), ('Ankle', 'Ankle'), ('Shoulder', 'Shoulder'),
        ('Wrist', 'Wrist'), ('Back', 'Back'), ('Hip', 'Hip'),
        ('Finger', 'Finger'), ('Elbow', 'Elbow'), ('Head', 'Head'), ('Other', 'Other'),
    ]

    player = models.ForeignKey(VolleyPlayer, on_delete=models.CASCADE, related_name='injuries')
    injury_type = models.CharField(max_length=50, choices=INJURY_TYPES)
    body_part = models.CharField(max_length=50, choices=BODY_PARTS)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    date_reported = models.DateField()
    expected_return = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    medical_notes = models.TextField(blank=True)
    reported_by = models.CharField(max_length=100)

    class Meta:
        ordering = ['-date_reported']
        verbose_name_plural = 'injuries'

    def __str__(self):
        return f"{self.player.name} - {self.injury_type} ({self.severity})"
