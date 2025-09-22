from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

# Валидация изображений (аватаров)
def validate_image(image):
    if image:
        if image.size > 2 * 1024 * 1024:  # 2 МБ
            raise ValidationError("Размер изображения не должен превышать 2MB")
        try:
            img = Image.open(image)
            if img.format not in ['JPEG', 'JPG', 'PNG', 'GIF']:
                raise ValidationError("Поддерживаются только форматы: JPEG, JPG, PNG, GIF")
        except Exception:
            raise ValidationError("Некорректный формат изображения")


# Профиль пользователя
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    GENRES = (
        ("action", "Action"),
        ("comedy", "Comedy"),
        ("drama", "Drama"),
        ("sci-fi", "Sci-Fi"),
        ("fantasy", "Fantasy"),
        ("horror", "Horror"),
        ("thriller", "Thriller"),
        ("romance", "Romance"),
        ("anime", "Anime"),
    )

    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
    )

    avatar = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        validators=[validate_image]
    )
    bio = models.TextField(blank=True, null=True, max_length=500, verbose_name="О себе")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Пол")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    # Подписки
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    # Избранное
    favorite_genres = models.ManyToManyField("Genre", blank=True, related_name="fans")
    favorite_movies = models.ManyToManyField("Movie", blank=True, related_name="liked_by")
    favorite_series = models.ManyToManyField("Series", blank=True, related_name="liked_by")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


# Жанры
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Фильмы
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    release_year = models.PositiveIntegerField()
    poster = models.ImageField(upload_to="movies/", blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name="movies")

    def __str__(self):
        return self.title


# Сериалы
class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    poster = models.ImageField(upload_to="series/", blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name="series")

    def __str__(self):
        return self.title


# Сигнал: создание профиля при создании пользователя
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
