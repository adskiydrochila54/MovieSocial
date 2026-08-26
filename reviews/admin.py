from django.contrib import admin

from .models import Comment, Review, ReviewLike


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "movie", "author", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("title", "content", "movie__title", "author__username")


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "author", "created_at")
    search_fields = ("content", "author__username")
