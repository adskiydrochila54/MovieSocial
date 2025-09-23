from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    photo = models.ImageField(upload_to='people/')

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)
    poster_image = models.ImageField(upload_to='movies/posters/', blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    actors = models.ManyToManyField(Person, related_name='acted_movies', blank=True)
    directors = models.ManyToManyField(Person, related_name='directed_movies', blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
