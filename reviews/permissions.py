from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Админы могут создавать/редактировать обзоры.
    Пользователи могут только читать.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
