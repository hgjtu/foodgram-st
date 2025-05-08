from django.urls import path
from .views import (
    recipe_list,
    recipe_detail,
    recipe_get_link,
    download_shopping_cart,
    shopping_cart,
    favorites,
    ingredient_list,
    ingredient_detail
)

urlpatterns = [
    path('', recipe_list, name='recipe-list'),  # GET and POST
    path('<int:id>/', recipe_detail, name='recipe-detail'),  # GET, PATCH, DELETE
    path('<int:id>/get-link/', recipe_get_link, name='recipe-get-link'),
    path('download_shopping_cart/', download_shopping_cart, name='download-shopping-cart'),
    path('<int:id>/shopping_cart/', shopping_cart, name='shopping-cart'),  # POST and DELETE
    path('<int:id>/favorite/', favorites, name='favorites'),  # POST and DELETE
    path('ingredients/', ingredient_list, name='ingredient-list'),
    path('ingredients/<int:id>/', ingredient_detail, name='ingredient-detail'),
]