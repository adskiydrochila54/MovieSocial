from django.contrib import admin
from .models import Review,ReviewLike,Comment

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

