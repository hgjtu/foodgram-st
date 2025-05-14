from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Ингредиент
class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField("Название ингредиента",
                            max_length=200, unique=True)
    measurement_unit = models.CharField(
        "Единица измерения", max_length=10)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"
