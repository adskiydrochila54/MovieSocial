from django.contrib import admin

from movies.models import Genre, Movie, Person, Series


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "created_at")
    search_fields = ("title", "description")
    list_filter = ("genres",)
    filter_horizontal = ("genres", "actors", "directors")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_date")
    search_fields = ("name",)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "start_year", "end_year")
    search_fields = ("title", "description")
    list_filter = ("genres",)
    filter_horizontal = ("genres", "actors", "directors")
