from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import News


class NewsApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="author@example.com", username="author", password="StrongPass123!"
        )
        self.other = User.objects.create_user(
            email="other@example.com", username="other", password="StrongPass123!"
        )
        self.published = News.objects.create(
            author=self.author, title="Published", content="Public", is_published=True
        )
        self.draft = News.objects.create(
            author=self.author, title="Draft", content="Private", is_published=False
        )

    def test_anonymous_only_sees_published_news(self):
        response = self.client.get(reverse("news-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["title"] for item in response.data["results"]], ["Published"])

    def test_author_sees_own_draft_and_other_cannot_change_news(self):
        self.client.force_authenticate(self.author)
        own_list = self.client.get(reverse("news-list"))
        self.assertEqual(len(own_list.data["results"]), 2)
        self.client.force_authenticate(self.other)
        update = self.client.patch(
            reverse("news-detail", args=[self.published.pk]), {"title": "Changed"}
        )
        hidden_draft = self.client.get(reverse("news-detail", args=[self.draft.pk]))
        self.assertEqual(update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(hidden_draft.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_forces_authenticated_author(self):
        self.client.force_authenticate(self.other)
        response = self.client.post(
            reverse("news-list"),
            {"title": "New", "content": "Body", "author": self.author.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(News.objects.get(title="New").author, self.other)
