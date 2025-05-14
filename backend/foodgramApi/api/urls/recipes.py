from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.recipes import RecipeViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
] 