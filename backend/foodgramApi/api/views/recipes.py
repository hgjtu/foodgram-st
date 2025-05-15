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
        return self._manage_recipe_list(request, recipe, user, 'favorites', 'избранном')

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        return self._manage_recipe_list(request, recipe, user, 'shopping_cart', 'списке покупок')

    def _manage_recipe_list(self, request, recipe, user, list_name, list_verbose_name):
        user_list = getattr(user, list_name)

        if request.method == 'POST':
            if user_list.filter(id=recipe.id).exists():
                return Response(
                    {"errors": f"Рецепт уже в {list_verbose_name}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_list.add(recipe)
            serializer = self.get_serializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            through_model_instance = get_object_or_404(
                user_list.through,
                user=user,
                recipe=recipe
            )
            through_model_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except user_list.through.DoesNotExist:
            return Response(
                {"errors": f"Рецепт не был в {list_verbose_name}."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in_shopping_carts=request.user)
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
