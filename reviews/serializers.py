from rest_framework import serializers

from .models import Comment, Review, ReviewLike


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["author"]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

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

    def validate(self, attrs):
        request = self.context.get("request")
        author = getattr(self.instance, "author", None) or getattr(request, "user", None)
        movie = attrs.get("movie", getattr(self.instance, "movie", None))
        queryset = Review.objects.filter(author=author, movie=movie)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if author and movie and queryset.exists():
            raise serializers.ValidationError({"movie": "You have already reviewed this movie."})
        return attrs


class ReviewLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLike
        fields = ["id", "review", "user", "created_at"]
        read_only_fields = ["user"]

    def validate_review(self, review):
        request = self.context.get("request")
        if request and ReviewLike.objects.filter(review=review, user=request.user).exists():
            raise serializers.ValidationError("You have already liked this review.")
        return review
