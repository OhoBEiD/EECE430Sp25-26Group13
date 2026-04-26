from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile
from .roles import Role


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={'role': Role.ADMIN if instance.is_superuser else Role.PLAYER},
    )
