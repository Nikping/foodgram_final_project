from django.urls import include, path
from rest_framework import routers

from api.views import (
    CustomUserViewSet,
    FollowListViewSet,
    FollowDestroyCreateViewSet,
    TagListRetrieveViewSet,
    IngredientViewSet,
    RecipeViewSet,
    FavoriteDestroyCreateViewSet,
    ShoppingCartDestroyCreateViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowDestroyCreateViewSet,
    basename='subscribe'
)
router.register(
    'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions'
)
router.register('users', CustomUserViewSet)
router.register('tags', TagListRetrieveViewSet)
router.register('recipes', RecipeViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartDestroyCreateViewSet,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteDestroyCreateViewSet,
    basename='favorite'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
