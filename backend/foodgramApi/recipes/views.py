from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from .models import Recipe, RecipeIngredient, Ingredient
from .serializers import (
    RecipeListSerializer, RecipeCreateSerializer,
    IngredientSerializer
)
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.http import HttpResponse

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def recipe_list(request):
    queryset = Recipe.objects.all()

    # Фильтрация по автору
    author_id = request.query_params.get('author')
    if author_id:
        queryset = queryset.filter(author_id=author_id)

    # Фильтрация по избранному
    is_favorited = request.query_params.get('is_favorited')
    if is_favorited and request.user.is_authenticated:
        if is_favorited == '1':
            queryset = queryset.filter(favorited_by=request.user)
        elif is_favorited == '0':
            queryset = queryset.exclude(favorited_by=request.user)

    # Фильтрация по списку покупок
    is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
    if is_in_shopping_cart and request.user.is_authenticated:
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(in_shopping_carts=request.user)
        elif is_in_shopping_cart == '0':
            queryset = queryset.exclude(in_shopping_carts=request.user)

    # Пагинация
    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = RecipeListSerializer(
        result_page,
        many=True,
        context={'request': request}
    )
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recipe_create(request):
    serializer = RecipeCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    recipe = serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    serializer = RecipeListSerializer(recipe, context={'request': request})
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def recipe_update(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, является ли пользователь автором рецепта
    if recipe.author != request.user:
        return Response(
            {"detail": "У вас недостаточно прав для выполнения данного действия."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = RecipeCreateSerializer(
        recipe,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    # Возвращаем обновленный рецепт в формате RecipeListSerializer
    response_serializer = RecipeListSerializer(recipe, context={'request': request})
    return Response(response_serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, является ли пользователь автором рецепта
    if recipe.author != request.user:
        return Response(
            {"detail": "У вас недостаточно прав для выполнения данного действия."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    recipe.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def recipe_get_link(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Генерируем короткую ссылку на основе id рецепта
    # Используем первые 3 символа хеша id для создания короткой ссылки
    hash_object = hashlib.md5(str(recipe.id).encode())
    short_hash = hash_object.hexdigest()[:3]
    
    # Формируем полную короткую ссылку
    short_link = f"https://foodgram.example.org/s/{short_hash}"
    
    return Response({"short-link": short_link})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    # Получаем все ингредиенты из рецептов в корзине пользователя
    ingredients = RecipeIngredient.objects.filter(
        recipe__in_shopping_carts=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        total_amount=Sum('amount')
    ).order_by('ingredient__name')

    # Создаем PDF файл
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Заголовок
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Список покупок")
    
    # Список ингредиентов
    p.setFont("Helvetica", 12)
    y = height - 100
    for item in ingredients:
        # Форматируем строку в соответствии с требуемым форматом
        text = f"{item['ingredient__name']} ({item['ingredient__measurement_unit']}) — {item['total_amount']}"
        p.drawString(50, y, text)
        y -= 20
        if y < 50:  # Если достигли конца страницы
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)

    p.save()
    buffer.seek(0)

    # Создаем HTTP ответ с PDF файлом
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_shopping_cart(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, не добавлен ли уже рецепт в корзину
    if recipe.in_shopping_carts.filter(id=request.user.id).exists():
        return Response(
            {"detail": "Рецепт уже добавлен в список покупок."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Добавляем рецепт в корзину
    recipe.in_shopping_carts.add(request.user)
    
    # Возвращаем данные рецепта в требуемом формате
    return Response({
        "id": recipe.id,
        "name": recipe.name,
        "image": request.build_absolute_uri(recipe.image.url) if recipe.image else None,
        "cooking_time": recipe.cooking_time
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_shopping_cart(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, есть ли рецепт в корзине
    if not recipe.in_shopping_carts.filter(id=request.user.id).exists():
        return Response(
            {"detail": "Рецепт не был в списке покупок."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Удаляем рецепт из корзины
    recipe.in_shopping_carts.remove(request.user)
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, не добавлен ли уже рецепт в избранное
    if recipe.favorited_by.filter(id=request.user.id).exists():
        return Response(
            {"detail": "Рецепт уже добавлен в избранное."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Добавляем рецепт в избранное
    recipe.favorited_by.add(request.user)
    
    # Возвращаем данные рецепта в требуемом формате
    return Response({
        "id": recipe.id,
        "name": recipe.name,
        "image": request.build_absolute_uri(recipe.image.url) if recipe.image else None,
        "cooking_time": recipe.cooking_time
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Проверяем, есть ли рецепт в избранном
    if not recipe.favorited_by.filter(id=request.user.id).exists():
        return Response(
            {"detail": "Рецепт не был в избранном."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Удаляем рецепт из избранного
    recipe.favorited_by.remove(request.user)
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_list(request):
    # Получаем параметр поиска
    name = request.query_params.get('name', '')
    
    # Базовый queryset
    queryset = Ingredient.objects.all()
    
    # Если есть параметр поиска, фильтруем по нему
    if name:
        queryset = queryset.filter(name__istartswith=name)
    
    # Сериализуем данные
    serializer = IngredientSerializer(queryset, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def ingredient_detail(request, id):
    # Получаем ингредиент по id
    ingredient = get_object_or_404(Ingredient, id=id)
    
    # Сериализуем данные
    serializer = IngredientSerializer(ingredient)
    
    return Response(serializer.data)
