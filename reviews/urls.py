from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ReviewViewSet, CommentViewSet, ReviewLikeViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet, basename="reviews")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"review-likes", ReviewLikeViewSet, basename="review-likes")

urlpatterns = [
    path("", include(router.urls)),
]
