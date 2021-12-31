from django.urls import include, path
from rest_framework import routers

from .views import (
    APISignup,
    APIToken,
    CategoryViewSet,
    CommentsViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UsersViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"genres", GenreViewSet, basename="genres")
router.register(r"titles", TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>[0-9]+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>\d+)/",
    ReviewViewSet,
    basename="reviews",
)
router.register(
    r"titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>\d+)/comments",
    CommentsViewSet,
    basename="comments",
)

urls = [
    path("auth/token/", APIToken.as_view(), name="api-token"),
    path("auth/signup/", APISignup.as_view(), name="api-signup"),
]

urls += router.urls

urlpatterns = [path("v1/", include(urls))]
