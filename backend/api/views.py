from datetime import datetime
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (
    filters,
    serializers,
    mixins,
    status,
    permissions,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import MyFilterSet, IngredientFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    TegSerializer,
    RecipeReadSerializer,
    FollowSerializer
)
from recipes.models import (
    Tag,
    Recipe,
    ShoppingCart,
    Favorite,
    Ingredient,
    IngredientToRecipe
)
from users.models import User, Follow


class CustomUserViewSet(UserViewSet):
    """Пользовательский view-класс."""

    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.all()


class FollowListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """View-класс для отображения списка модели Follow."""

    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowDestroyCreateViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """View-класс для создания и удаления модели Follow."""

    serializer_class = FollowSerializer
    queryset = User.objects.all()

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        author = get_object_or_404(User, pk=user_id)
        instance = Follow.objects.filter(
            user=request.user, author=author
        )
        if not instance:
            raise serializers.ValidationError(
                'Вы ещё не оформили подписку на этого пользователя!'
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """View-класс для отображения ингредиента или списка ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class ShoppingCartDestroyCreateViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """View-класс для cоздания и удаления объекта ShoppingCart."""

    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        instance = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        )
        if not instance:
            raise serializers.ValidationError(
                'В корзине нет такого списка продуктов!'
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteDestroyCreateViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """View-класс для создания и удаления объекта Favorite."""

    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        instance = Favorite.objects.filter(
            user=request.user, recipe=recipe
        )
        if not instance:
            raise serializers.ValidationError(
                'В избранном нет такого рецепта!'
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """View-класс для отображения одного тегов или списка тегов"""

    queryset = Tag.objects.all()
    serializer_class = TegSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """View-класс для отображения и создания рецептов."""

    permission_classes = (IsAuthorOrReadOnly, )
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    filter_class = MyFilterSet
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """Скачивание товаров из корзины."""
        ingredients = IngredientToRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        today = datetime.today()
        shopping_cart = (
            f'Сегодня {today.day}/{today.month}/{today.year}\n'
            f'В магазине необходимо купить:\n'
        )
        for ingredient in ingredients:
            shopping_cart += (
                f"\n - {ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']})"
                f" - {ingredient['amount']}")
        shopping_cart += f'\n\n by FoodgramCollection {today.year}'
        filename = f'{request.user.username}_shopping_list.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = \
            f'attachment; filename="{filename}.txt"'
        return response
