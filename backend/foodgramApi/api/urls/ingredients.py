from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.ingredients import IngredientViewSet

app_name = 'ingredients'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
] 