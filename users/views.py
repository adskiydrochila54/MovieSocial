from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Profile, Genre, Movie, Series
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    GenreSerializer,
    MovieSerializer,
    SeriesSerializer,
    RegisterSerializer,
    LoginSerializer,
)

User = get_user_model()

# ================== USERS ==================
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ================== PROFILES ==================
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk=None):
        profile = self.get_object()
        if profile == request.user.profile:
            return Response({"error": "Нельзя подписаться на себя"}, status=status.HTTP_400_BAD_REQUEST)
        if profile in request.user.profile.following.all():
            return Response({"error": "Вы уже подписаны"}, status=status.HTTP_400_BAD_REQUEST)
        request.user.profile.following.add(profile)
        return Response({"message": f"Вы подписались на {profile.user.username}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        if profile not in request.user.profile.following.all():
            return Response({"error": "Вы не подписаны"}, status=status.HTTP_400_BAD_REQUEST)
        request.user.profile.following.remove(profile)
        return Response({"message": f"Вы отписались от {profile.user.username}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        profile = self.get_object()
        followers = profile.followers.all().select_related("user")
        serializer = UserSerializer([p.user for p in followers], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        profile = self.get_object()
        following = profile.following.all().select_related("user")
        serializer = UserSerializer([p.user for p in following], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def friends(self, request, pk=None):
        profile = self.get_object()
        friends = profile.following.filter(following=profile).select_related("user")
        serializer = UserSerializer([p.user for p in friends], many=True)
        return Response(serializer.data)

# ================== GENRES ==================
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# ================== MOVIES ==================
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# ================== SERIES ==================
class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# ================== AUTH ==================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Успешный вход",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Требуется refresh токен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Помещаем токен в blacklist
            return Response({"message": "Вы вышли из аккаунта"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Невалидный или просроченный токен"}, status=status.HTTP_400_BAD_REQUEST)
