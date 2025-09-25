from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet, ProfileViewSet, GenreViewSet, MovieViewSet, SeriesViewSet,
    RegisterView, LoginView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'profiles', ProfileViewSet, basename='profiles')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'movies', MovieViewSet, basename='movies')
router.register(r'series', SeriesViewSet, basename='series')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
]
