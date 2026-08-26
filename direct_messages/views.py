from django.db.models import Prefetch
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Chat, DirectMessage
from .permissions import IsParticipant
from .serializers import ChatCreateSerializer, ChatSerializer, DirectMessageSerializer


class ChatViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Chat.objects.none()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_serializer_class(self):
        if self.action == "create":
            return ChatCreateSerializer
        return ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user).prefetch_related(
            "participants",
            Prefetch(
                "messages",
                queryset=DirectMessage.objects.select_related("sender").order_by("-created_at"),
                to_attr="prefetched_messages",
            ),
        )


class DirectMessageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = DirectMessage.objects.none()
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return DirectMessage.objects.filter(chat__participants=self.request.user).select_related(
            "chat", "sender"
        )

    def perform_create(self, serializer):
        chat_id = self.request.data.get("chat")
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            raise PermissionDenied("Чат не найден")

        if self.request.user not in chat.participants.all():
            raise PermissionDenied("Вы не участник этого чата")

        serializer.save(sender=self.request.user, chat=chat)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.sender_id == request.user.id:
            raise ValidationError({"detail": "A sender cannot mark their own message as read."})
        message.is_read = True
        message.save(update_fields=["is_read"])
        return Response(status=status.HTTP_204_NO_CONTENT)
