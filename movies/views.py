from rest_framework import viewsets
from .models import Movie, Genre, Person
from .serializers import MovieSerializer, GenreSerializer, PersonSerializer
from .permissions import IsAdminOrReadOnly

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAdminOrReadOnly]


from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Comment
from .forms import CommentForm

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    comments = movie.comments.order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.author = request.user
            comment.save()
            return redirect('movie_detail', pk=movie.pk)
    else:
        form = CommentForm()

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'comments': comments,
        'form': form
    })

