from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Ingredient
from .serializers import IngredientSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def ingredient_list(request):
    name = request.query_params.get("name", "")
    queryset = Ingredient.objects.all()

    if name:
        queryset = queryset.filter(name__istartswith=name)

    serializer = IngredientSerializer(queryset, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def ingredient_detail(request, id):
    ingredient = get_object_or_404(Ingredient, id=id)
    serializer = IngredientSerializer(ingredient)
    return Response(serializer.data)
