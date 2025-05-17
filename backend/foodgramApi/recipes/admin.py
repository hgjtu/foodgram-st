from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cooking_time", "author", "favorite_count", "ingredients_display", "image_display")
    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__last_name",
    )
    list_filter = ("author", "created")
    inlines = [RecipeIngredientInline]
    readonly_fields = ("favorite_count",)
    fieldsets = (
        (None, {"fields": ("name", "author",
                           "image", "text", "cooking_time")}),
        ("Статистика", {"fields": ("favorite_count",)}),
    )

    @admin.display(description="Добавлений в избранное")
    def favorite_count(self, recipe):
        return recipe.favorited_by_users_relations.count()

    @admin.display(description="Продукты")
    def ingredients_display(self, recipe):
        ingredients = recipe.recipe_ingredients.all()
        if not ingredients.exists():
            return "Нет продуктов"
        
        html_parts = []
        for item in ingredients:
            html_parts.append(f"<li>{item.ingredient.name}: {item.amount}</li>")
        
        html_ul = f"<ul>{''.join(html_parts)}</ul>"
        return mark_safe(html_ul)

    @admin.display(description="Картинка")
    def image_display(self, recipe):
        if recipe.image and hasattr(recipe.image, 'url'):
            return mark_safe(f'<img src="{recipe.image.url}" style="max-width: 70px; max-height: 70px; object-fit: cover;" />')
        return "Нет изображения"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")
    list_filter = ("recipe", "ingredient")
