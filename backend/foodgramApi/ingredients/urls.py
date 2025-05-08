from django.urls import path
from .views import ingredient_list, ingredient_detail

urlpatterns = [
    path('', ingredient_list, name='ingredient-list'),
    path('<int:id>/', ingredient_detail, name='ingredient-detail'),
] 