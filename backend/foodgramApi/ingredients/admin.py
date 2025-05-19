from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", "recipe_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit", )
    ordering = ("name",)

    @admin.display(description="Число рецептов")
    def recipe_count(self, ingredient):
        return ingredient.recipes.count()
