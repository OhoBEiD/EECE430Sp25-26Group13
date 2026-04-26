from django.db import migrations


SEED_ROLES = {
    'manager_sara': 'manager',
    'coach_ahmad': 'coach',
    'scout_layla': 'scout',
    'player_omar': 'player',
    'admin_volleyhub': 'admin',
}


def backfill_roles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')

    for user in User.objects.all():
        target_role = SEED_ROLES.get(user.username)
        if target_role is None and user.is_superuser:
            target_role = 'admin'
        if target_role is None:
            target_role = 'player'

        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': target_role},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_roles, noop_reverse),
    ]
