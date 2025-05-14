from django.urls import path
from api.views.recipes import (
    recipe_list_create,
    recipe_detail,
    recipe_favorite,
    recipe_shopping_cart,
    download_shopping_cart
)

app_name = 'recipes'

urlpatterns = [
    path('recipes/', recipe_list_create, name='recipe-list'),
    path('recipes/<int:pk>/', recipe_detail, name='recipe-detail'),
    path('recipes/<int:pk>/favorite/', recipe_favorite, name='recipe-favorite'),
    path('recipes/<int:pk>/shopping_cart/', recipe_shopping_cart, name='recipe-shopping-cart'),
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download-shopping-cart'),
] 