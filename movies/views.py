from rest_framework import viewsets

from .models import Genre, Movie, Person, Series
from .permissions import IsAdminOrReadOnly
from .serializers import GenreSerializer, MovieSerializer, PersonSerializer, SeriesSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.prefetch_related("genres", "actors", "directors")
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["genres", "actors", "directors", "release_date"]
    search_fields = ["title", "description", "actors__name", "directors__name"]
    ordering_fields = ["title", "release_date", "created_at"]
    ordering = ["-release_date", "title"]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name", "birth_date"]
    ordering = ["name"]


class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.prefetch_related("genres", "actors", "directors")
    serializer_class = SeriesSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["genres", "actors", "directors", "start_year", "end_year"]
    search_fields = ["title", "description", "actors__name", "directors__name"]
    ordering_fields = ["title", "start_year", "end_year", "created_at"]
    ordering = ["-start_year", "title"]
