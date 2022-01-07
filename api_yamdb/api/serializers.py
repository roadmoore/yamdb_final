from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=250, required=True)
    confirmation_code = serializers.CharField(max_length=250, required=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_username(self, username):
        if username == "me":
            raise serializers.ValidationError("Username не может быть me")
        return username


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            self.context["request"].user.is_authenticated
            and self.context["request"].user.is_user
        ):
            self.fields.get("role").read_only = True

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("id",)


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        required=False,
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
        required=False,
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Title

    def validate_year(self, value):
        year = timezone.now().year
        if not value <= year:
            raise serializers.ValidationError(
                "Год выпуска не может быть больше текущего"
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(read_only=True, slug_field="id")

    class Meta:
        model = Review
        fields = "__all__"

    def validate(self, value):
        request = self.context["request"]
        title_id = self.context.get("view").kwargs.get("title_id")
        author = request.user
        title = get_object_or_404(Title, pk=title_id)
        if request.method == "POST":
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    "Можно оставить только один отзыв!"
                )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    review = serializers.SlugRelatedField(read_only=True, slug_field="text")

    class Meta:
        fields = "__all__"
        model = Comment
