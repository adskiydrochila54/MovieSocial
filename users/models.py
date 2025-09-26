from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from PIL import Image


# ---------- Пользователь ----------
class UserManager(BaseUserManager):
    """Менеджер пользователей"""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email")
        if not username:
            raise ValueError("Пользователь должен иметь username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    # Права
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username} - {self.email}"


# ---------- Валидация изображения ----------
def validate_image(image):
    """Валидатор для аватарок/постеров"""
    if image:
        if image.size > 2 * 1024 * 1024:  # > 2 MB
            raise ValidationError("Размер изображения не должен превышать 2MB")

        try:
            img = Image.open(image)
            if img.format not in ["JPEG", "JPG", "PNG", "GIF"]:
                raise ValidationError("Поддерживаются только JPEG, JPG, PNG, GIF")
        except Exception:
            raise ValidationError("Некорректный формат изображения")


# ---------- Профиль ----------
class Profile(models.Model):
    """Профиль пользователя"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Основное
    avatar = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
        validators=[validate_image],
    )
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="О себе")

    # Дополнительно
    GENDER_CHOICES = (
        ("M", "Мужской"),
        ("F", "Женский"),
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Пол"
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    # Подписки/друзья
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )

    # Интересы
    favorite_genres = models.ManyToManyField("Genre", blank=True, related_name="fans")
    favorite_movies = models.ManyToManyField("Movie", blank=True, related_name="liked_by")
    favorite_series = models.ManyToManyField("Series", blank=True, related_name="liked_by")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

    # Удобные методы
    def is_following(self, profile):
        """Проверяет, подписан ли пользователь на другого"""
        return self.following.filter(id=profile.id).exists()

    def is_friends_with(self, profile):
        """Проверяет, дружат ли (взаимная подписка)"""
        return self.is_following(profile) and profile.is_following(self)


# ---------- Жанры ----------
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# ---------- Фильмы ----------
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    release_year = models.PositiveIntegerField()
    poster = models.ImageField(upload_to="movies/", blank=True, null=True, validators=[validate_image])
    genres = models.ManyToManyField(Genre, related_name="movies")

    def __str__(self):
        return self.title


# ---------- Сериалы ----------
class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    poster = models.ImageField(upload_to="series/", blank=True, null=True, validators=[validate_image])
    genres = models.ManyToManyField(Genre, related_name="series")

    def __str__(self):
        return self.title


# ---------- Сигналы ----------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаем профиль при регистрации"""
    if created:
        Profile.objects.create(user=instance)
