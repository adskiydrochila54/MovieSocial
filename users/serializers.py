from rest_framework import serializers
from .models import User, Profile, Genre, Movie, Series


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'joined_date']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'username', 'email']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_year', 'poster', 'genres']


class SeriesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'title', 'description', 'start_year', 'end_year', 'poster', 'genres']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_movies = MovieSerializer(many=True, read_only=True)
    favorite_series = SeriesSerializer(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'avatar',
            'bio',
            'gender',
            'birth_date',
            'following',
            'followers_count',
            'following_count',
            'favorite_genres',
            'favorite_movies',
            'favorite_series',
            'created_at',
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
