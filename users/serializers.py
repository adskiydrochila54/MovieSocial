from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Profile, Genre, Movie, Series


# ---------- USER ----------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "joined_date"]


# ---------- GENRES ----------
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


# ---------- MOVIES ----------
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_year", "poster", "genres"]


# ---------- SERIES ----------
class SeriesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ["id", "title", "description", "start_year", "end_year", "poster", "genres"]


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

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "avatar",
            "bio",
            "gender",
            "birth_date",
            "following",
            "followers",
            "followers_count",
            "following_count",
            "favorite_genres",
            "favorite_movies",
            "favorite_series",
            "created_at",
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_following(self, obj):
        """Список на кого подписан"""
        return [f.user.username for f in obj.following.all()]

    def get_followers(self, obj):
        """Список подписчиков"""
        return [f.user.username for f in obj.followers.all()]


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
        # на всякий случай создаём профиль, если сигнал не сработал
        if not hasattr(user, "profile"):
            Profile.objects.create(user=user)
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

from rest_framework import serializers
from .models import Profile


class FriendSerializer(serializers.ModelSerializer):
    """Мини-сериализатор профиля (для друзей/подписок/подписчиков)"""
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "email", "avatar"]


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
