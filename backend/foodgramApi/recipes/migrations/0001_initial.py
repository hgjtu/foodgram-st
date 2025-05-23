# Generated by Django 5.2.1 on 2025-05-08 13:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                (
                    "image",
                    models.ImageField(
                        upload_to="recipes/images/", verbose_name="Картинка"
                    ),
                ),
                ("text", models.TextField(verbose_name="Описание")),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Время приготовления (в минутах)",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата публикации"
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент рецепта",
                "verbose_name_plural": "Ингредиенты рецепта",
            },
        ),
    ]
