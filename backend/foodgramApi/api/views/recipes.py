from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Sum, Exists, OuterRef
from ..models import Favorite, ShoppingCart
from recipes.models import Recipe, RecipeIngredient
from ..serializers.recipes import (
    RecipeListSerializer,
    RecipeCreateSerializer,
    ShortRecipeSerializer,
    RecipeGetShortLinkSerializer,
)
import hashlib
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.urls import NoReverseMatch

User = get_user_model()


class RecipePagination(PageNumberPagination):
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
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateSerializer
        if self.action in ['favorite', 'shopping_cart'] and self.request.method == 'POST':
            return ShortRecipeSerializer
        if self.action == 'get_link':
            return RecipeGetShortLinkSerializer
        return RecipeListSerializer

    def get_permissions(self):
        if self.action in ['create', 'favorite', 'shopping_cart', 'download_shopping_cart']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        elif self.action == 'get_link':
            self.permission_classes = [AllowAny]
        else:
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
            is_favorited_param = request.query_params.get("is_favorited")
            if is_favorited_param == "1":
                queryset = queryset.filter(id__in=Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True))
            elif is_favorited_param == "0":
                queryset = queryset.exclude(id__in=Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True))

            is_in_shopping_cart_param = request.query_params.get("is_in_shopping_cart")
            if is_in_shopping_cart_param == "1":
                queryset = queryset.filter(id__in=ShoppingCart.objects.filter(user=request.user).values_list('recipe_id', flat=True))
            elif is_in_shopping_cart_param == "0":
                queryset = queryset.exclude(id__in=ShoppingCart.objects.filter(user=request.user).values_list('recipe_id', flat=True))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_entry = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite_entry.exists():
            return Response(
                {"errors": "Рецепт не был в избранном."},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_entry = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not cart_entry.exists():
            return Response(
                {"errors": "Рецепт не был в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipe_ids = ShoppingCart.objects.filter(user=request.user).values_list('recipe_id', flat=True)
        
        ingredients = (
            RecipeIngredient.objects.filter(recipe_id__in=recipe_ids)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        html = render_to_string("shopping_list.html", {"ingredients": ingredients})

        pdf_file = HTML(string=html, encoding="utf-8").write_pdf()

        response = FileResponse(pdf_file, as_attachment=True, filename="shopping_list.pdf", content_type="application/pdf")
        return response

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='get-link', url_name='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        try:
            short_hash = hex(recipe.pk)[2:]

            reversed_short_link_path = reverse('api:public-recipe-detail', kwargs={'pk': short_hash})
            short_link = request.build_absolute_uri(reversed_short_link_path)
        except NoReverseMatch:
            return Response({"error": "URL for short link resolver is not configured correctly. Check 'api:public-recipe-detail' URL name."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except TypeError:
             return Response({"error": "Invalid recipe ID for hashing."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(data={"short-link": short_link})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
