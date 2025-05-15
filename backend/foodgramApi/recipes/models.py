from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MinLengthValidator

from ingredients.models import Ingredient

User = get_user_model()

MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1
MIN_RECIPE_NAME_LENGTH = 1
MIN_RECIPE_TEXT_LENGTH = 1


# Рецепт
class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="recipes", verbose_name="Автор"
    )
    name = models.CharField(
        "Название",
        max_length=200,
        validators=[MinLengthValidator(MIN_RECIPE_NAME_LENGTH)]
    )
    image = models.ImageField("Картинка", upload_to="recipes/images/")
    text = models.TextField(
        "Описание",
        validators=[MinLengthValidator(MIN_RECIPE_TEXT_LENGTH)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления (в минутах)", validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created",)

    def __str__(self):
        return self.name


# Связь рецепта и ингредиента
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        "ingredients.Ingredient",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        "Количество", validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)]
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )
