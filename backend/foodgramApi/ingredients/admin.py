from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "get_measurement_unit_display", "recipe_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit", )
    ordering = ("name",)

    def get_measurement_unit_display(self, ingredient):
        return ingredient.get_measurement_unit_display()

    get_measurement_unit_display.short_description = "Единица измерения"

    def recipe_count(self, ingredient):
        return ingredient.recipes.count()

    recipe_count.short_description = "Число рецептов"
