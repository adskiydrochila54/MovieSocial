from rest_framework import permissions


class IsSenderOrReceiver(permissions.BasePermission):
    """
    Доступ к сообщению только у отправителя или получателя
    """

    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.receiver == request.user
