from io import BytesIO
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
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
    ShortRecipeSerializer
)
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import Http404, FileResponse
from django.urls import reverse

from django_filters.rest_framework import DjangoFilterBackend
import django_filters

User = get_user_model()

class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(favorite__user=user)
        return queryset.exclude(favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(shoppingcart__user=user)
        return queryset.exclude(shoppingcart__user=user)

class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 100

    list_filter = ("author", "is_favorited", "is_in_shopping_cart", )


class IsAuthorOrReadOnly(BasePermission):    
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateSerializer
        if self.action in ['favorite', 'shopping_cart'] and self.request.method == 'POST':
            return ShortRecipeSerializer 
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
        

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._handle_recipe_action(
            request, pk, Favorite, "избранном", "favorite"
        )

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._handle_recipe_action(
            request, pk, ShoppingCart, "списке покупок", "shopping_cart"
        )

    def _handle_recipe_action(self, request, pk, model, error_message, action_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": f"Рецепт «{recipe.name}» уже в {error_message}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        entry = model.objects.filter(user=user, recipe=recipe)
        if not entry.exists():
            return Response(
                {"errors": f"Рецепт «{recipe.name}» не был в {error_message}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        entry.delete()
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

        pdf_file = BytesIO(HTML(string=html, encoding="utf-8").write_pdf())

        response = FileResponse(pdf_file, as_attachment=True, filename="shopping_list.pdf", content_type="application/pdf")
        return response

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='get-link', url_name='get-link')
    def get_link(self, request, pk=None):
        reversed_path = reverse('api:public-recipe-detail', kwargs={'pk': pk})
        short_link = request.build_absolute_uri(reversed_path)

        return Response(
            {"short-link": short_link},
            status=status.HTTP_200_OK
        )
        
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='s', url_name='short')
    def short_link(self, request, hash=None):
        recipe = get_object_or_404(Recipe, pk=hash)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

