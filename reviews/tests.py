from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from movies.models import Movie
from users.models import User

from .models import Comment, Review, ReviewLike


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="author@example.com", username="author", password="StrongPass123!"
        )
        self.other = User.objects.create_user(
            email="other@example.com", username="other", password="StrongPass123!"
        )
        self.movie = Movie.objects.create(title="Arrival")

    def create_review(self):
        return Review.objects.create(
            movie=self.movie,
            author=self.author,
            title="Great",
            content="Excellent movie",
            rating=5,
        )

    def test_authenticated_user_can_create_review_once(self):
        self.client.force_authenticate(self.author)
        payload = {
            "movie": self.movie.pk,
            "title": "Great",
            "content": "Excellent movie",
            "rating": 5,
        }
        first = self.client.post(reverse("reviews-list"), payload)
        second = self.client.post(reverse("reviews-list"), payload)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_user_cannot_change_review_or_comment(self):
        review = self.create_review()
        comment = Comment.objects.create(review=review, author=self.author, content="Owner comment")
        self.client.force_authenticate(self.other)
        review_update = self.client.patch(
            reverse("reviews-detail", args=[review.pk]), {"title": "Stolen"}
        )
        comment_delete = self.client.delete(reverse("comments-detail", args=[comment.pk]))
        self.assertEqual(review_update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(comment_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_is_unique_and_private_to_owner(self):
        review = self.create_review()
        self.client.force_authenticate(self.author)
        first = self.client.post(reverse("review-likes-list"), {"review": review.pk})
        second = self.client.post(reverse("review-likes-list"), {"review": review.pk})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        like = ReviewLike.objects.get()
        self.client.force_authenticate(self.other)
        response = self.client.delete(reverse("review-likes-detail", args=[like.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_response_contains_comments_and_like_count(self):
        review = self.create_review()
        Comment.objects.create(review=review, author=self.other, content="Nice")
        ReviewLike.objects.create(review=review, user=self.other)
        response = self.client.get(reverse("reviews-detail", args=[review.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["likes_count"], 1)
        self.assertEqual(len(response.data["comments"]), 1)
