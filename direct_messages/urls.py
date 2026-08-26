from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatViewSet, DirectMessageViewSet

router = DefaultRouter()
router.register(r"chats", ChatViewSet, basename="chats")
router.register(r"messages", DirectMessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]
