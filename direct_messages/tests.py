from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Chat, DirectMessage


class DirectMessageApiTests(APITestCase):
    def setUp(self):
        self.first = User.objects.create_user(
            email="first@example.com", username="first", password="StrongPass123!"
        )
        self.second = User.objects.create_user(
            email="second@example.com", username="second", password="StrongPass123!"
        )
        self.outsider = User.objects.create_user(
            email="outside@example.com", username="outside", password="StrongPass123!"
        )

    def create_chat(self):
        chat = Chat.objects.create()
        chat.participants.add(self.first, self.second)
        return chat

    def test_chat_rejects_self_and_duplicate(self):
        self.client.force_authenticate(self.first)
        self_chat = self.client.post(reverse("chats-list"), {"participants": [self.first.pk]})
        self.assertEqual(self_chat.status_code, status.HTTP_400_BAD_REQUEST)
        first = self.client.post(reverse("chats-list"), {"participants": [self.second.pk]})
        duplicate = self.client.post(reverse("chats-list"), {"participants": [self.second.pk]})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_outsider_cannot_read_chat_or_send_message(self):
        chat = self.create_chat()
        self.client.force_authenticate(self.outsider)
        detail = self.client.get(reverse("chats-detail", args=[chat.pk]))
        send = self.client.post(reverse("messages-list"), {"chat": chat.pk, "content": "Secret"})
        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(send.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_message_is_rejected_and_recipient_can_mark_read(self):
        chat = self.create_chat()
        self.client.force_authenticate(self.first)
        empty = self.client.post(reverse("messages-list"), {"chat": chat.pk, "content": "   "})
        self.assertEqual(empty.status_code, status.HTTP_400_BAD_REQUEST)
        created = self.client.post(reverse("messages-list"), {"chat": chat.pk, "content": "Hello"})
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        message = DirectMessage.objects.get()
        sender_mark = self.client.post(reverse("messages-mark-read", args=[message.pk]))
        self.assertEqual(sender_mark.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.force_authenticate(self.second)
        recipient_mark = self.client.post(reverse("messages-mark-read", args=[message.pk]))
        self.assertEqual(recipient_mark.status_code, status.HTTP_204_NO_CONTENT)
        message.refresh_from_db()
        self.assertTrue(message.is_read)
