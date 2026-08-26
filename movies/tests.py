from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Genre, Movie, Person, Series


class CatalogApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="StrongPass123!"
        )
        self.user = User.objects.create_user(
            email="user@example.com", username="user", password="StrongPass123!"
        )
        self.genre = Genre.objects.create(name="Drama")
        self.person = Person.objects.create(name="Director")

    def test_anonymous_can_read_catalog_but_user_cannot_write(self):
        Movie.objects.create(title="Arrival", release_date=date(2016, 9, 1))
        listing = self.client.get(reverse("movie-list"))
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(self.user)
        create = self.client.post(
            reverse("movie-list"),
            {"title": "Dune", "release_date": "2021-10-22", "genre_ids": [self.genre.pk]},
        )
        self.assertEqual(create.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_movie_with_relations(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse("movie-list"),
            {
                "title": "Dune",
                "release_date": "2021-10-22",
                "genre_ids": [self.genre.pk],
                "director_ids": [self.person.pk],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(title="Dune")
        self.assertEqual(list(movie.genres.all()), [self.genre])
        self.assertEqual(list(movie.directors.all()), [self.person])

    def test_series_rejects_end_year_before_start_year(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse("series-list"),
            {
                "title": "Broken timeline",
                "start_year": 2025,
                "end_year": 2020,
                "genre_ids": [self.genre.pk],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Series.objects.exists())
