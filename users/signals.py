from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, Genre


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

        default_genres = Genre.objects.filter(name__in=["Драма", "Комедия"])
        profile.favorite_genres.set(default_genres)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
