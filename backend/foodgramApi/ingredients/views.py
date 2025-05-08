from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Ingredient
from .serializers import IngredientSerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_list(request):
    # Get search parameter
    name = request.query_params.get('name', '')
    
    # Base queryset
    queryset = Ingredient.objects.all()
    
    # Filter by name if provided
    if name:
        queryset = queryset.filter(name__istartswith=name)
    
    # Serialize data
    serializer = IngredientSerializer(queryset, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_detail(request, id):
    ingredient = get_object_or_404(Ingredient, id=id)
    serializer = IngredientSerializer(ingredient)
    return Response(serializer.data)
