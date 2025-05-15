from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Sum
from recipes.models import Recipe, RecipeIngredient, User
from ..serializers.recipes import (
    RecipeListSerializer,
    RecipeCreateSerializer,
    ShortRecipeSerializer,
)
import hashlib
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateSerializer
        # For 'favorite' and 'shopping_cart' POST, we use ShortRecipeSerializer
        # The list and retrieve actions use RecipeListSerializer by default (can be specified too)
        if self.action in ['favorite', 'shopping_cart'] and self.request.method == 'POST':
            return ShortRecipeSerializer
        return RecipeListSerializer # Default for list, retrieve

    def get_permissions(self):
        if self.action in ['create', 'favorite', 'shopping_cart', 'download_shopping_cart']:
            # Create, favorite, shopping_cart require authentication
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'update', 'destroy']:
            # Modifying/deleting a recipe requires being the author or admin
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            # List, retrieve are AllowAny
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        author_id = request.query_params.get("author")
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        if request.user.is_authenticated:
            is_favorited = request.query_params.get("is_favorited")
            if is_favorited == "1":
                queryset = queryset.filter(favorited_by=request.user)
            elif is_favorited == "0":
                queryset = queryset.exclude(favorited_by=request.user)

            is_in_shopping_cart = request.query_params.get("is_in_shopping_cart")
            if is_in_shopping_cart == "1":
                queryset = queryset.filter(in_shopping_carts=request.user)
            elif is_in_shopping_cart == "0":
                queryset = queryset.exclude(in_shopping_carts=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user.favorites.filter(id=recipe.id).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.add(recipe)
            serializer = self.get_serializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # DELETE request
        if not user.favorites.filter(id=recipe.id).exists():
            return Response(
                {"errors": "Рецепт не был в избранном."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user.shopping_cart.filter(id=recipe.id).exists(): # Assuming 'shopping_cart' is the related_name on User model
                return Response(
                    {"errors": "Рецепт уже в списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.shopping_cart.add(recipe)
            serializer = self.get_serializer(recipe, context={'request': request}) # Uses ShortRecipeSerializer due to get_serializer_class logic
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE request
        if not user.shopping_cart.filter(id=recipe.id).exists():
            return Response(
                {"errors": "Рецепт не был в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in_shopping_carts=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        # Ensure 'shopping_list.html' template exists and is configured
        html = render_to_string("shopping_list.html", {"ingredients": ingredients})
        # Ensure weasyprint is installed and wkhtmltopdf (or alternative) is available if needed by weasyprint
        pdf_file = HTML(string=html, encoding="utf-8").write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.pdf"'
        return response
