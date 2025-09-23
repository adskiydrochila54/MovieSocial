from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MovieViewSet, GenreViewSet, PersonViewSet

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"genres", GenreViewSet)
router.register(r"people", PersonViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
