import os
from datetime import date

from django.core.management.base import BaseCommand

from movies.models import Genre, Movie, Person, Series
from news.models import News
from reviews.models import Review
from users.models import User


class Command(BaseCommand):
    help = "Create an idempotent portfolio demo dataset."

    def handle(self, *args, **options):
        genres = {
            name: Genre.objects.get_or_create(name=name)[0]
            for name in ("Drama", "Science Fiction", "Thriller")
        }
        director, _ = Person.objects.get_or_create(
            name="Denis Villeneuve", defaults={"birth_date": date(1967, 10, 3)}
        )
        movie, _ = Movie.objects.get_or_create(
            title="Arrival",
            release_date=date(2016, 11, 11),
            defaults={
                "description": "A linguist works with the military to communicate with aliens."
            },
        )
        movie.genres.set([genres["Drama"], genres["Science Fiction"]])
        movie.directors.add(director)

        series, _ = Series.objects.get_or_create(
            title="Movix Demo Series",
            start_year=2024,
            defaults={"description": "Demo content for exploring the API."},
        )
        series.genres.set([genres["Drama"], genres["Thriller"]])

        password = os.getenv("MOVIX_DEMO_PASSWORD", "DemoPass123!")
        user, created = User.objects.get_or_create(
            email="demo@movix.local", defaults={"username": "demo"}
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        user.profile.favorite_movies.add(movie)
        user.profile.favorite_series.add(series)

        Review.objects.get_or_create(
            movie=movie,
            author=user,
            defaults={
                "title": "Thought-provoking science fiction",
                "content": "A strong example of character-driven science fiction.",
                "rating": 5,
            },
        )
        News.objects.get_or_create(
            author=user,
            title="Welcome to Movix",
            defaults={
                "content": "Explore movies, reviews, profiles and private conversations.",
                "is_published": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Login: demo@movix.local")
        self.stdout.write("Password: value of MOVIX_DEMO_PASSWORD (default: DemoPass123!)")
