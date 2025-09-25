from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ChatViewSet, DirectMessageViewSet

router = DefaultRouter()
router.register(r"chats", ChatViewSet, basename="chats")
router.register(r"messages", DirectMessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]
