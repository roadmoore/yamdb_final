from django_filters import rest_framework as filterset

from reviews.models import Title


class TitlesFilter(filterset.FilterSet):
    category = filterset.CharFilter(
        field_name="category__slug", lookup_expr="icontains"
    )
    genre = filterset.CharFilter(
        field_name="genre__slug", lookup_expr="icontains"
    )
    name = filterset.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Title
        fields = ("category", "genre", "name", "year")
