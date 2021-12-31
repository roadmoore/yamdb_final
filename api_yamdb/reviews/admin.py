from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User

admin.site.register(User)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "year",
        "description",
        "category",
    )
    search_fields = ("name",)
    filter_horizontal = ("genre",)
    list_filter = ("year",)
    empty_value_display = "-пусто-"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "author",
        "pub_date",
        "title",
        "score",
    )
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "author",
        "review",
        "pub_date",
        "created",
    )
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
