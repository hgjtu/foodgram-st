from django.urls import path
from .views import (
    recipe_list,
    recipe_detail,
    recipe_get_link,
    download_shopping_cart,
    shopping_cart,
    favorites
)

urlpatterns = [
    path('', recipe_list, name='recipe-list'),
    path('<int:id>/', recipe_detail, name='recipe-detail'),
    path('<int:id>/get-link/', recipe_get_link, name='recipe-get-link'),
    path('download_shopping_cart/', download_shopping_cart, name='download-shopping-cart'),
    path('<int:id>/shopping_cart/', shopping_cart, name='shopping-cart'),
    path('<int:id>/favorite/', favorites, name='favorites'),
]