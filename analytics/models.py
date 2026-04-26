from django.conf import settings
from django.db import models
from players.models import VolleyPlayer


class PlayerStats(models.Model):
    player = models.ForeignKey(VolleyPlayer, on_delete=models.CASCADE, related_name='stats')
    date_recorded = models.DateField()
    serve_accuracy = models.IntegerField(help_text='0-100')
    spike_success = models.IntegerField(help_text='0-100')
    block_rate = models.IntegerField(help_text='0-100')
    dig_success = models.IntegerField(help_text='0-100')
    set_accuracy = models.IntegerField(help_text='0-100')
    receive_rating = models.IntegerField(help_text='0-100')
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_stats',
    )

    class Meta:
        ordering = ['-date_recorded']
        verbose_name_plural = 'player stats'

    def __str__(self):
        return f"{self.player.name} - {self.date_recorded}"

    @property
    def overall_score(self):
        return round((self.serve_accuracy + self.spike_success + self.block_rate +
                      self.dig_success + self.set_accuracy + self.receive_rating) / 6)
