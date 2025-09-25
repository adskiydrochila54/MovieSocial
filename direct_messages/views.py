from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Chat, DirectMessage
from .serializers import ChatSerializer, DirectMessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        participants_ids = self.request.data.get("participants", [])
        if not participants_ids or len(participants_ids) != 2:
            raise PermissionDenied("Чат должен быть только между двумя пользователями")

        serializer.save()
        serializer.instance.participants.add(*participants_ids)


class DirectMessageViewSet(viewsets.ModelViewSet):
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

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
