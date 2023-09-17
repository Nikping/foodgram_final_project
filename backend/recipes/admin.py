from django.contrib import admin

from backend.settings import EMPTY_FIELD_VALUE
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientToRecipe,
    Favorite,
    ShoppingCart
)


class IngredientInline(admin.TabularInline):
    """Встроенное представление
    для редактирования ингредиентов в админ. панели.
    """
    model = IngredientToRecipe
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели рецептов/
    Также включает список рецептов, поиск и фильтрацию по тегам.
    """
    list_display = (
        'author',
        'name',
        'cooking_time'
    )
    search_fields = (
        'author__username',
        'author__email',
        'name'
    )
    list_filter = ('tags',)
    inlines = (IngredientInline,)


class TegAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели тегов."""
    list_display = (
        'name',
        'color',
        'slug',
    )
    empty_value_display = EMPTY_FIELD_VALUE


class IngredientAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели ингредиентов."""
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = EMPTY_FIELD_VALUE


class IngredientToRecipeAdmin(admin.ModelAdmin):
    """Настройки админ. панели связывающей модели ингредиентов и рецептов."""
    list_display = (
        'ingredient',
        'recipe',
        'amount',
    )
    search_fields = (
        'ingredient__name',
        'recipe__name'
    )
    list_filter = ('recipe__tags',)
    empty_value_display = EMPTY_FIELD_VALUE


class FavoriteAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели избранных рецептов."""
    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('recipe__tags__name',)
    search_fields = (
        'user__email',
        'user__username',
        'recipe__name'
    )
    empty_value_display = EMPTY_FIELD_VALUE


class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки админ. панели для модели корзины покупок."""
    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__email',
        'user__username',
        'recipe__name'
    )
    list_filter = ('recipe__tags',)
    empty_value_display = EMPTY_FIELD_VALUE


admin.site.register(Tag, TegAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientToRecipe, IngredientToRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
