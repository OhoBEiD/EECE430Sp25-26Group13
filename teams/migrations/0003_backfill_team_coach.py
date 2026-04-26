from django.db import migrations


def backfill_team_coach(apps, schema_editor):
    Team = apps.get_model('teams', 'Team')
    User = apps.get_model('auth', 'User')

    for team in Team.objects.all():
        if team.coach_id is not None or not team.coach_name:
            continue

        label = team.coach_name.strip()
        if label.lower().startswith('coach '):
            label = label[len('coach '):].strip()
        tokens = [t for t in label.split() if t]
        if not tokens:
            continue

        match = (
            User.objects.filter(username__iexact=label).first()
            or User.objects.filter(last_name__iexact=tokens[-1]).first()
            or User.objects.filter(first_name__iexact=tokens[0]).first()
        )
        if match is not None:
            team.coach = match
            team.save(update_fields=['coach'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_team_coach_alter_team_coach_name'),
        ('accounts', '0002_backfill_demo_roles'),
    ]

    operations = [
        migrations.RunPython(backfill_team_coach, noop_reverse),
    ]
