from rest_framework import serializers
from .models import Chat, DirectMessage


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ["id", "chat", "sender", "content", "created_at", "is_read"]
        read_only_fields = ["sender", "created_at", "is_read"]


class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at", "last_message"]

    def get_last_message(self, obj):
        msg = obj.last_message()
        if msg:
            return DirectMessageSerializer(msg).data
        return None
