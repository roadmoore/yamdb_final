from django.db.models import Func
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import RefreshToken


class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 2)"


class GenreCategoryMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
