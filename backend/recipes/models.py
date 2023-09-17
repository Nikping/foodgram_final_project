from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator
)
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега'
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message="Неверный формат тега или такого цвета не существует."
            )
        ]
    )
    slug = models.SlugField(
        verbose_name='Slug тега',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецептов."""
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientToRecipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='api/',
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name='Текст рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            RegexValidator(
                regex=r'^[0-9]+$',
                message="Время приготовления должно быть числом."
            ),
            MinValueValidator(
                1,
                message="Время приготовления должно быть больше 0."
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id', )

    def __str__(self):
        return f'{self.name} автор: {self.author.get_username()}'


class IngredientToRecipe(models.Model):
    """Модель связки рецепта и ингредиента."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredienttorecipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            RegexValidator(
                regex=r'^[0-9]+$',
                message="Количество ингредиента должно быть числом."
            ), MinValueValidator(
                1,
                message="Количество ингредиента должно быть больше 0."
            ), MaxValueValidator(
                50000,
                message="Количество ингредиента должно быть меньше 50000."
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f'Связь ингредиента {self.ingredient.name} и рецепта: '
            f'{self.recipe.name}'
        )


class Favorite(models.Model):
    """Модель добавление в избраное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorites',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_favorite_unique'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f'Избранный рецепт {self.recipe.name} пользователя: '
            f'{self.user.get_username}'
        )


class ShoppingCart(models.Model):
    """ Модель списка покупок. """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_shopping_unique'
            )
        ]
        verbose_name = 'Товар в корзине',
        verbose_name_plural = 'Товары в корзине'
        ordering = ('user',)

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} в списке покупок пользователя: '
            f'{self.user.get_username}'
        )
