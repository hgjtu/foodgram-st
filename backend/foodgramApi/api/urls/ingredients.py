from django.urls import path
from api.views.ingredients import ingredient_list, ingredient_detail

app_name = 'ingredients'

urlpatterns = [
    path('ingredients/', ingredient_list, name='ingredient-list'),
    path('ingredients/<int:pk>/', ingredient_detail, name='ingredient-detail'),
] 