from rest_framework import serializers
from .models import Review, Comment, ReviewLike

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["author"]

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "movie",
            "author",
            "title",
            "content",
            "rating",
            "created_at",
            "comments",
            "likes_count",
        ]
        read_only_fields = ["author"]

    def get_likes_count(self, obj):
        return obj.likes.count()

class ReviewLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLike
        fields = ["id", "review", "user", "created_at"]
        read_only_fields = ["user"]