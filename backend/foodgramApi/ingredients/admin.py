from django.contrib import admin
from .models import Ingredient

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_measurement_unit_display')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    ordering = ('name',)

    def get_measurement_unit_display(self, obj):
        return obj.get_measurement_unit_display()
    get_measurement_unit_display.short_description = 'Единица измерения'
