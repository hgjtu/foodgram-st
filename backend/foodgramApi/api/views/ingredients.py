from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ingredients.models import Ingredient
from api.serializers.ingredients import IngredientSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny] 