from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Доступ к сообщению или чату только если пользователь участвует в чате
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "participants"):  # для Chat
            return request.user in obj.participants.all()
        elif hasattr(obj, "chat"):  # для DirectMessage
            return request.user in obj.chat.participants.all()
        return False
