from datetime import date

from django.db import migrations, models


def move_catalog_and_favorites(apps, schema_editor):
    OldGenre = apps.get_model("users", "Genre")
    OldMovie = apps.get_model("users", "Movie")
    OldSeries = apps.get_model("users", "Series")
    Profile = apps.get_model("users", "Profile")
    Genre = apps.get_model("movies", "Genre")
    Movie = apps.get_model("movies", "Movie")
    Series = apps.get_model("movies", "Series")

    genre_map = {}
    for old_genre in OldGenre.objects.all():
        genre, _ = Genre.objects.get_or_create(name=old_genre.name)
        genre_map[old_genre.pk] = genre

    movie_map = {}
    for old_movie in OldMovie.objects.prefetch_related("genres"):
        movie, _ = Movie.objects.get_or_create(
            title=old_movie.title,
            release_date=date(old_movie.release_year, 1, 1),
            defaults={
                "description": old_movie.description or "",
                "poster_image": old_movie.poster,
            },
        )
        movie.genres.add(
            *(genre_map[genre.pk] for genre in old_movie.genres.all())
        )
        movie_map[old_movie.pk] = movie

    series_map = {}
    for old_series in OldSeries.objects.prefetch_related("genres"):
        series, _ = Series.objects.get_or_create(
            title=old_series.title,
            start_year=old_series.start_year,
            defaults={
                "description": old_series.description or "",
                "end_year": old_series.end_year,
                "poster_image": old_series.poster,
            },
        )
        series.genres.add(
            *(genre_map[genre.pk] for genre in old_series.genres.all())
        )
        series_map[old_series.pk] = series

    for profile in Profile.objects.prefetch_related(
        "favorite_genres", "favorite_movies", "favorite_series"
    ):
        profile.migrated_favorite_genres.add(
            *(genre_map[item.pk] for item in profile.favorite_genres.all())
        )
        profile.migrated_favorite_movies.add(
            *(movie_map[item.pk] for item in profile.favorite_movies.all())
        )
        profile.migrated_favorite_series.add(
            *(series_map[item.pk] for item in profile.favorite_series.all())
        )


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0002_series_alter_genre_options_alter_movie_options_and_more"),
        ("users", "0002_alter_movie_poster_alter_profile_gender_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="migrated_favorite_genres",
            field=models.ManyToManyField(
                blank=True, related_name="favorited_by", to="movies.genre"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="migrated_favorite_movies",
            field=models.ManyToManyField(
                blank=True, related_name="favorited_by", to="movies.movie"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="migrated_favorite_series",
            field=models.ManyToManyField(
                blank=True, related_name="favorited_by", to="movies.series"
            ),
        ),
        migrations.RunPython(move_catalog_and_favorites, migrations.RunPython.noop),
        migrations.RemoveField(model_name="profile", name="favorite_genres"),
        migrations.RemoveField(model_name="profile", name="favorite_movies"),
        migrations.RemoveField(model_name="profile", name="favorite_series"),
        migrations.RenameField(
            model_name="profile",
            old_name="migrated_favorite_genres",
            new_name="favorite_genres",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="migrated_favorite_movies",
            new_name="favorite_movies",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="migrated_favorite_series",
            new_name="favorite_series",
        ),
        migrations.DeleteModel(name="Movie"),
        migrations.DeleteModel(name="Genre"),
        migrations.DeleteModel(name="Series"),
    ]
