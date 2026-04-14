from django.db import models


class VolleyPlayer(models.Model):
    name = models.CharField(max_length=100)
    date_joined = models.DateField()
    position = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    contact_person = models.CharField(max_length=100)
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    photo = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Relative path under static/, e.g. 'players/portraits/p1.jpg'",
    )

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper() if self.name else '??'
