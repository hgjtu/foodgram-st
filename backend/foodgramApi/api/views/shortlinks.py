from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from recipes.models import Recipe
from ..serializers.recipes import RecipeListSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404

class ShortLinkRecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles requests for recipes via short links.
    Retrieves and displays a recipe using its PK (decoded from hash) from the short link.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        short_hash = self.kwargs.get(self.lookup_url_kwarg)

        if not short_hash:
            raise Http404("Short hash not found in URL.")

        try:
            recipe_id = int(short_hash, 16)
        except ValueError:
            raise Http404(f"Invalid short hash format: {short_hash}")

        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=recipe_id)

        # Проверяем права доступа к объекту (хотя у нас AllowAny, это хорошая практика)
        self.check_object_permissions(self.request, obj)
        return obj