from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewLikeViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet, basename="reviews")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"review-likes", ReviewLikeViewSet, basename="review-likes")

urlpatterns = [
    path("", include(router.urls)),
]
