from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from teams.models import Event

from .models import Notification


@receiver(post_save, sender=Event)
def notify_team_on_new_event(sender, instance: Event, created: bool, **kwargs):
    if not created:
        return

    from accounts.models import UserProfile
    profiles = (
        UserProfile.objects
        .filter(linked_player__team_id=instance.team_id)
        .select_related('user')
    )

    notifications = []
    email_recipients = []
    title = f'New {instance.event_type}: {instance.title}'
    body = (
        f'{instance.team.name} has a new {instance.event_type.lower()} on '
        f'{instance.date:%A, %B %d} at {instance.start_time:%I:%M %p} — {instance.location}.'
    )
    link = f'/teams/event/{instance.pk}/'

    for profile in profiles:
        notifications.append(Notification(
            user=profile.user,
            kind=Notification.KIND_EVENT,
            title=title,
            body=body,
            link=link,
        ))
        if profile.user.email:
            email_recipients.append(profile.user.email)

    if notifications:
        Notification.objects.bulk_create(notifications)

    if email_recipients:
        send_mail(
            subject=f'[VolleyHub] {title}',
            message=f'{body}\n\nView details: {link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_recipients,
            fail_silently=True,
        )
