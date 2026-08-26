from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from movies.models import Genre, Movie, Series

from .models import User


class UserApiTests(APITestCase):
    def create_user(self, email="user@example.com", username="user"):
        return User.objects.create_user(email=email, username=username, password="StrongPass123!")

    def test_registration_creates_user_profile_and_hashes_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "new@example.com",
                "username": "new-user",
                "password": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertTrue(hasattr(user, "profile"))

    def test_login_refresh_and_private_me_endpoint(self):
        user = self.create_user()
        login = self.client.post(
            reverse("login"),
            {"email": user.email, "password": "StrongPass123!"},
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        refresh = self.client.post(reverse("token-refresh"), {"refresh": login.data["refresh"]})
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        me = self.client.get(reverse("users-me"))
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], user.email)

    def test_public_user_does_not_expose_email(self):
        user = self.create_user()
        response = self.client.get(reverse("users-detail", args=[user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("email", response.data)

    def test_user_cannot_update_or_delete_another_profile(self):
        owner = self.create_user()
        attacker = self.create_user("other@example.com", "other")
        self.client.force_authenticate(attacker)
        update = self.client.patch(
            reverse("profiles-detail", args=[owner.profile.pk]), {"bio": "changed"}
        )
        delete = self.client.delete(reverse("profiles-detail", args=[owner.profile.pk]))
        self.assertEqual(update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_follow_and_unfollow(self):
        user = self.create_user()
        target = self.create_user("target@example.com", "target")
        self.client.force_authenticate(user)
        follow = self.client.post(reverse("profiles-follow", args=[target.profile.pk]))
        self.assertEqual(follow.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(user.profile.following.filter(pk=target.profile.pk).exists())
        unfollow = self.client.delete(reverse("profiles-unfollow", args=[target.profile.pk]))
        self.assertEqual(unfollow.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(user.profile.following.filter(pk=target.profile.pk).exists())

    def test_user_cannot_follow_self(self):
        user = self.create_user()
        self.client.force_authenticate(user)
        response = self.client.post(reverse("profiles-follow", args=[user.profile.pk]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_favorites_without_exposing_birth_date(self):
        user = self.create_user()
        genre = Genre.objects.create(name="Drama")
        movie = Movie.objects.create(title="Arrival")
        series = Series.objects.create(title="Demo", start_year=2024)
        self.client.force_authenticate(user)

        response = self.client.patch(
            reverse("profiles-detail", args=[user.profile.pk]),
            {
                "birth_date": "2000-01-01",
                "favorite_genre_ids": [genre.pk],
                "favorite_movie_ids": [movie.pk],
                "favorite_series_ids": [series.pk],
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("birth_date", response.data)
        self.assertIsInstance(response.data["age"], int)
        user.profile.refresh_from_db()
        self.assertEqual(list(user.profile.favorite_movies.all()), [movie])

    def test_logout_blacklists_refresh_token(self):
        user = self.create_user()
        login = self.client.post(
            reverse("login"),
            {"email": user.email, "password": "StrongPass123!"},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        logout = self.client.post(reverse("logout"), {"refresh": login.data["refresh"]})
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)

        self.client.credentials()
        refresh = self.client.post(reverse("token-refresh"), {"refresh": login.data["refresh"]})
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)
