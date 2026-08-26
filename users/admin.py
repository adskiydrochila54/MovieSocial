from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "username", "is_staff", "is_active", "joined_date")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (("Contact", {"fields": ("email",)}),)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "created_at")
    search_fields = ("user__email", "user__username", "bio")
    filter_horizontal = ("following", "favorite_genres", "favorite_movies", "favorite_series")
