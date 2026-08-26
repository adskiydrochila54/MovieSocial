from django.contrib import admin

from .models import Chat, DirectMessage


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    filter_horizontal = ("participants",)


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ("chat", "sender", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__username")
