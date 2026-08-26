from django.core.exceptions import ValidationError
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="people/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)
    poster_image = models.ImageField(upload_to="movies/posters/", blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    actors = models.ManyToManyField(Person, related_name="acted_movies", blank=True)
    directors = models.ManyToManyField(Person, related_name="directed_movies", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_date", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "release_date"], name="unique_movie_title_release_date"
            )
        ]

    def __str__(self):
        return self.title


class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    poster_image = models.ImageField(upload_to="series/posters/", blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name="series")
    actors = models.ManyToManyField(Person, related_name="acted_series", blank=True)
    directors = models.ManyToManyField(Person, related_name="directed_series", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_year", "title"]
        verbose_name_plural = "series"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "start_year"], name="unique_series_title_start_year"
            )
        ]

    def clean(self):
        if self.end_year is not None and self.end_year < self.start_year:
            raise ValidationError({"end_year": "End year cannot be earlier than start year."})

    def __str__(self):
        return self.title
