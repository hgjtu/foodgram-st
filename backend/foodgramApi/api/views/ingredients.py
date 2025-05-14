from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ingredients.models import Ingredient
from api.serializers.ingredients import IngredientSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_list(request):
    """List all ingredients."""
    ingredients = Ingredient.objects.all()
    serializer = IngredientSerializer(ingredients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_detail(request, pk):
    """Retrieve a single ingredient."""
    try:
        ingredient = Ingredient.objects.get(pk=pk)
    except Ingredient.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = IngredientSerializer(ingredient)
    return Response(serializer.data) 