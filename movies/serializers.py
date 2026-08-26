from rest_framework import serializers

from .models import Genre, Movie, Person, Series


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "birth_date", "photo"]


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = PersonSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        source="genres", queryset=Genre.objects.all(), many=True, write_only=True
    )
    actor_ids = serializers.PrimaryKeyRelatedField(
        source="actors", queryset=Person.objects.all(), many=True, write_only=True, required=False
    )
    director_ids = serializers.PrimaryKeyRelatedField(
        source="directors",
        queryset=Person.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "release_date",
            "poster_image",
            "genres",
            "actors",
            "directors",
            "genre_ids",
            "actor_ids",
            "director_ids",
        ]


class SeriesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = PersonSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        source="genres", queryset=Genre.objects.all(), many=True, write_only=True
    )
    actor_ids = serializers.PrimaryKeyRelatedField(
        source="actors", queryset=Person.objects.all(), many=True, write_only=True, required=False
    )
    director_ids = serializers.PrimaryKeyRelatedField(
        source="directors",
        queryset=Person.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Series
        fields = [
            "id",
            "title",
            "description",
            "start_year",
            "end_year",
            "poster_image",
            "genres",
            "actors",
            "directors",
            "genre_ids",
            "actor_ids",
            "director_ids",
        ]

    def validate(self, attrs):
        start_year = attrs.get("start_year", getattr(self.instance, "start_year", None))
        end_year = attrs.get("end_year", getattr(self.instance, "end_year", None))
        if end_year is not None and start_year is not None and end_year < start_year:
            raise serializers.ValidationError(
                {"end_year": "End year cannot be earlier than start year."}
            )
        return attrs
