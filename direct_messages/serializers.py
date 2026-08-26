from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Chat, DirectMessage

User = get_user_model()


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ["id", "chat", "sender", "content", "created_at", "is_read"]
        read_only_fields = ["sender", "created_at", "is_read"]

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        return value


class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at", "last_message"]

    @extend_schema_field(DirectMessageSerializer(allow_null=True))
    def get_last_message(self, obj) -> dict | None:
        msg = obj.last_message()
        if msg:
            return DirectMessageSerializer(msg).data
        return None


class ChatCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_participants(self, participants):
        request = self.context["request"]
        if len(participants) != 1:
            raise serializers.ValidationError("Specify exactly one other participant.")
        other_user = participants[0]
        if other_user == request.user:
            raise serializers.ValidationError("You cannot create a chat with yourself.")
        existing_chat = (
            Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
        )
        if existing_chat:
            raise serializers.ValidationError(f"Chat {existing_chat.pk} already exists.")
        return participants

    def create(self, validated_data):
        participants = validated_data.pop("participants")
        chat = Chat.objects.create(**validated_data)
        chat.participants.add(self.context["request"].user, participants[0])
        return chat
