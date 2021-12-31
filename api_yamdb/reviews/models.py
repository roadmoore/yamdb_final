from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.fields.related import ManyToManyField

from .validators import year_validator


class User(AbstractUser):
    US = "user"
    MD = "moderator"
    AD = "admin"
    USER_ROLES_CHOICES = (
        (US, "user"),
        (MD, "moderator"),
        (AD, "admin"),
    )

    email = models.EmailField(
        max_length=254,
        verbose_name="Электропочта",
        blank=False,
        unique=True,
    )

    bio = models.TextField(
        verbose_name="Биография",
        blank=True,
    )

    role = models.CharField(
        verbose_name="Роль",
        max_length=254,
        choices=USER_ROLES_CHOICES,
        default=US,
    )

    confirmation_code = models.CharField(
        verbose_name="Confirmation code",
        max_length=30,
        blank=True,
        editable=False,
        null=True,
        unique=True,
    )

    @property
    def is_user(self):
        return self.role == self.US

    @property
    def is_moderator(self):
        return self.role == self.MD

    @property
    def is_admin(self):
        return self.role == self.AD


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Категория")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название жанра")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256, verbose_name="Название произведения"
    )
    year = models.IntegerField(
        validators=[year_validator], verbose_name="Год выхода"
    )
    description = models.TextField(verbose_name="Описание")
    genre = ManyToManyField(Genre, verbose_name="Жанры")
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="titles",
        verbose_name="Категории",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10, message="Оценка не может быть больше 10"),
            MinValueValidator(1, message="Оценка не может быть меньше 1"),
        ],
        verbose_name="Оценка",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )

    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_reviews"
            )
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Рецензия",
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    text = models.TextField(verbose_name="Текст")
    created = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
