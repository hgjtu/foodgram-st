from django.urls import path
from .views import (
    recipe_list, recipe_create, recipe_detail, recipe_update,
    recipe_delete, recipe_get_link, download_shopping_cart,
    add_to_shopping_cart, remove_from_shopping_cart,
    add_to_favorites, remove_from_favorites, ingredient_list,
    ingredient_detail
)

urlpatterns = [
    path('', recipe_list, name='recipe-list'),
    path('', recipe_create, name='recipe-create'),
    path('<int:id>/', recipe_detail, name='recipe-detail'),
    path('<int:id>/', recipe_update, name='recipe-update'),
    path('<int:id>/', recipe_delete, name='recipe-delete'),
    path('<int:id>/get-link/', recipe_get_link, name='recipe-get-link'),
    path('download_shopping_cart/', download_shopping_cart, name='download-shopping-cart'),
    path('<int:id>/shopping_cart/', add_to_shopping_cart, name='add-to-shopping-cart'),
    path('<int:id>/shopping_cart/', remove_from_shopping_cart, name='remove-from-shopping-cart'),
    path('<int:id>/favorite/', add_to_favorites, name='add-to-favorites'),
    path('<int:id>/favorite/', remove_from_favorites, name='remove-from-favorites'),
    path('ingredients/', ingredient_list, name='ingredient-list'),
    path('ingredients/<int:id>/', ingredient_detail, name='ingredient-detail'),
]