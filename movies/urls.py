from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GenreViewSet, MovieViewSet, PersonViewSet, SeriesViewSet

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"genres", GenreViewSet)
router.register(r"people", PersonViewSet)
router.register(r"series", SeriesViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
