from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Chat, DirectMessage
from .serializers import ChatSerializer, DirectMessageSerializer
from .permissions import IsParticipant

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        participants_ids = self.request.data.get("participants", [])
        if not participants_ids or len(participants_ids) != 1:
            raise PermissionDenied("Вы должны указать одного другого участника для чата")

        other_user_id = participants_ids[0]
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            raise PermissionDenied("Пользователь не найден")

        chat = serializer.save()
        chat.participants.add(self.request.user, other_user)


class DirectMessageViewSet(viewsets.ModelViewSet):
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return DirectMessage.objects.filter(chat__participants=self.request.user)

    def perform_create(self, serializer):
        chat_id = self.request.data.get("chat")
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            raise PermissionDenied("Чат не найден")

        if self.request.user not in chat.participants.all():
            raise PermissionDenied("Вы не участник этого чата")

        serializer.save(sender=self.request.user, chat=chat)
