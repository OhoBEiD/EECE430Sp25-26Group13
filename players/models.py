from django.db import models


class VolleyPlayer(models.Model):
    name = models.CharField(max_length=100)
    date_joined = models.DateField()
    position = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    contact_person = models.CharField(max_length=100)
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    def __str__(self):
        return self.name
