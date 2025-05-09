from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorite_count")
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

    def favorite_count(self, obj):
        return obj.favorited_by.count()

    favorite_count.short_description = "Добавлений в избранное"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")
    list_filter = ("recipe", "ingredient")
