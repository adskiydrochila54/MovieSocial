from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = Profile.objects.get_or_create(user=instance)

        from movies.models import Genre

        default_genres = Genre.objects.filter(name__in=["Драма", "Комедия"])
        profile.favorite_genres.set(default_genres)
