from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
import base64
from django.core.files.base import ContentFile
from recipes.models import Recipe

User = get_user_model()


class CustomUserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False


class UserWithRecipesSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, obj):
        from .recipes import ShortRecipeSerializer
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except (TypeError, ValueError):
                recipes_limit = 3
        else:
            recipes_limit = 3

        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True, context={'request': request}).data 