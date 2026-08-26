from django.db.models import Count
from rest_framework import mixins, permissions, viewsets

from .models import Comment, Review, ReviewLike
from .permissions import IsAuthorOrAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import CommentSerializer, ReviewLikeSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = (
        Review.objects.select_related("movie", "author")
        .prefetch_related("comments__author")
        .annotate(likes_count=Count("likes", distinct=True))
    )
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdminOrReadOnly]
    filterset_fields = ["movie", "author", "rating"]
    search_fields = ["title", "content", "movie__title", "author__username"]
    ordering_fields = ["created_at", "rating", "likes_count"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("review", "author")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdminOrReadOnly]
    filterset_fields = ["review", "author"]
    search_fields = ["content", "author__username"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReviewLikeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ReviewLike.objects.none()
    serializer_class = ReviewLikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        queryset = ReviewLike.objects.select_related("review", "user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
