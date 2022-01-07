from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from reviews.models import Category, Comment, Genre, Review, Title, User

from api_yamdb import settings

from .filters import TitlesFilter
from .permissions import (CommentsAndReviewsPermission, IsAdminOrReadOnly,
                          UsersPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          EmailSerializer, GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)
from .utils import GenreCategoryMixin, Round, get_tokens_for_user


class APIToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data["username"]
        )
        serializer_code = serializer.validated_data["confirmation_code"]
        if user.confirmation_code == serializer_code:
            return Response(
                get_tokens_for_user(user), status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APISignup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            "Код для регистрации.",
            f"Код: {confirmation_code}.",
            settings.DEFAULT_FROM_EMAIL,
            [serializer.validated_data["email"]],
        )
        resp = {"email": email, "username": username}
        return Response(resp, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UsersPermission,)
    pagination_class = PageNumberPagination
    lookup_field = "username"

    @action(
        methods=[
            "get",
            "patch",
        ],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer,
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Round(Avg("reviews__score")))
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleReadSerializer
        return TitleSerializer


class GenreViewSet(GenreCategoryMixin):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ["name"]
    filterset_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(GenreCategoryMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ["name"]
    filterset_fields = ("name",)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (CommentsAndReviewsPermission,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (CommentsAndReviewsPermission,)
    queryset = Comment.objects.all()
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)
