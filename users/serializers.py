from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from movies.models import Genre, Movie, Series
from movies.serializers import GenreSerializer, MovieSerializer, SeriesSerializer

from .models import Profile, User


# ---------- USER ----------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "joined_date"]


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "joined_date"]
        read_only_fields = fields


# ---------- PROFILE ----------
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_movies = MovieSerializer(many=True, read_only=True)
    favorite_series = SeriesSerializer(many=True, read_only=True)

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    birth_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    age = serializers.SerializerMethodField()
    favorite_genre_ids = serializers.PrimaryKeyRelatedField(
        source="favorite_genres",
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    favorite_movie_ids = serializers.PrimaryKeyRelatedField(
        source="favorite_movies",
        queryset=Movie.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    favorite_series_ids = serializers.PrimaryKeyRelatedField(
        source="favorite_series",
        queryset=Series.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "avatar",
            "bio",
            "gender",
            "birth_date",
            "age",
            "following",
            "followers",
            "followers_count",
            "following_count",
            "favorite_genres",
            "favorite_movies",
            "favorite_series",
            "favorite_genre_ids",
            "favorite_movie_ids",
            "favorite_series_ids",
            "created_at",
        ]

    def get_followers_count(self, obj) -> int:
        return obj.followers.count()

    def get_following_count(self, obj) -> int:
        return obj.following.count()

    def get_following(self, obj) -> list[str]:
        """Список на кого подписан"""
        return [f.user.username for f in obj.following.all()]

    def get_followers(self, obj) -> list[str]:
        """Список подписчиков"""
        return [f.user.username for f in obj.followers.all()]

    def get_age(self, obj) -> int | None:
        if not obj.birth_date:
            return None
        today = timezone.localdate()
        return (
            today.year
            - obj.birth_date.year
            - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        )


# ---------- REGISTER ----------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


# ---------- LOGIN ----------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs.get("email"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)


class FriendSerializer(serializers.ModelSerializer):
    """Мини-сериализатор профиля (для друзей/подписок/подписчиков)"""

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "avatar"]


class FriendsListSerializer(serializers.ModelSerializer):
    """Расширенный сериализатор профиля с подписками/друзьями"""

    followers = FriendSerializer(many=True, read_only=True)
    following = FriendSerializer(many=True, read_only=True)
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "user", "followers", "following", "friends"]

    def get_friends(self, obj):
        """Друзья = только взаимные подписки"""
        mutual = obj.following.filter(id__in=obj.followers.values_list("id", flat=True))
        return FriendSerializer(mutual, many=True).data
