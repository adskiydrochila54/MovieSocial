from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = News
        fields = [
            'id',
            'author',
            'author_name',
            'title',
            'content',
            'image',
            'created_at',
            'updated_at',
            'is_published'
        ]
