from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404

from recipes.models import (
    Tag, Recipe, Ingredient,
    IngredientToRecipe, ShoppingCart, Favorite
)
from users.models import User, Follow
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import SerializerMethodField


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CustomUserSerializer(UserSerializer):
    """Сериализатор для обработки данных пользователей."""

    is_subscribed = SerializerMethodField()

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return Follow.objects.filter(
            user=current_user.id,
            author=obj.id
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки данных ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TegSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShortResipeSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощённого отображения рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(ShortResipeSerializer):
    """Сериализатор для обработки данных списка покупок."""

    def validate(self, data):
        request = self.context.get('request', None)
        current_recipe_id = self.context.get('request').parser_context.get(
            'kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=current_recipe_id)

        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок!'
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request', None)
        current_user = request.user
        current_recipe_id = self.context.get('request').parser_context.get(
            'kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=current_recipe_id)
        ShoppingCart.objects.create(user=current_user, recipe=recipe)
        return recipe


class FavoriteSerializer(ShortResipeSerializer):
    """Сериализатор для обработки данных избранных рецептов."""

    def validate(self, data):
        request = self.context.get('request', None)
        current_recipe_id = self.context.get('request').parser_context.get(
            'kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=current_recipe_id)

        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в избранные рецепты!'
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request', None)
        current_user = request.user
        current_recipe_id = self.context.get('request').parser_context.get(
            'kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=current_recipe_id)
        Favorite.objects.create(user=current_user, recipe=recipe)
        return recipe


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки данных
    связующей модели ингредиентов и рецептов.
    """

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientToRecipe
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки данных рецептов."""

    tags = serializers.SerializerMethodField()
    ingredients = IngredientToRecipeSerializer(
        many=True,
        source='ingredienttorecipe')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    read_only_fields = (
        'id',
        'author',
        'is_favorited',
        'is_favorited'
    )

    def get_tags(self, obj):
        return TegSerializer(
            Tag.objects.filter(recipes=obj),
            many=True
        ).data

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return ShoppingCart.objects.filter(
            user=current_user.id,
            recipe=obj.id,
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return Favorite.objects.filter(
            user=current_user.id,
            recipe=obj.id
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientToRecipeSerializer(
        many=True,
        source='ingredienttorecipe')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        request = self.context.get('request', None)
        tags_list = []
        ingredients_list = []
        request_methods = ['POST', 'PATCH']

        if request.method in request_methods:
            if 'tags' in data:
                tags = data['tags']
                for tag in tags:
                    if tag.id in tags_list:
                        raise serializers.ValidationError(
                            f'Тег {tag} повторяется'
                        )
                    tags_list.append(tag.id)
                if len(tags_list) == 0:
                    raise serializers.ValidationError(
                            'Должен присутствовать хотя бы 1 тег!'
                        )
                all_tags = Tag.objects.all().values_list('id', flat=True)
                if not set(tags_list).issubset(all_tags):
                    raise serializers.ValidationError(
                        f'Тега {tag} не существует!'
                    )
            if 'ingredienttorecipe' in data:
                ingredients = data['ingredienttorecipe']
                for ingredient in ingredients:
                    ingredient = ingredient['ingredient'].get('id')
                    if ingredient in ingredients_list:
                        raise serializers.ValidationError(
                            f'Ингредиент {ingredient} уже был добавлен!'
                        )
                    ingredients_list.append(ingredient)
                all_ingredients = Ingredient.objects.all().values_list(
                    'id', flat=True
                )
                if not set(ingredients_list).issubset(all_ingredients):
                    raise serializers.ValidationError(
                        'Указанного ингредиента не существует'
                    )
                if len(ingredients_list) == 0:
                    raise serializers.ValidationError(
                            'Список ингредиентов не должен быть пустым'
                        )
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_obj = Ingredient.objects.get(
                id=ingredient_data.get('ingredient')['id'])
            ingredient_liist.append(
                IngredientToRecipe(
                    ingredient=ingredient_obj,
                    amount=ingredient_data.get('amount'),
                    recipe=recipe,
                )
            )
        IngredientToRecipe.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredienttorecipe')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientToRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredienttorecipe')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
                 'request': self.context.get('request')
            }).data


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для обработки данных ингредиентов."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            queryset = Recipe.objects.filter(
                author=obj).order_by('-id')[:int(limit)]
        else:
            queryset = Recipe.objects.filter(author=obj)
        return ShortResipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def create(self, validated_data):
        request = self.context.get('request', None)
        author_id = self.context.get('request').parser_context.get(
            'kwargs').get('user_id')
        current_user = request.user
        author = get_object_or_404(User, pk=author_id)
        Follow.objects.create(user=current_user, author=author)
        return author
