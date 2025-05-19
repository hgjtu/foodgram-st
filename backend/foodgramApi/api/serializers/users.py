from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
import base64
from django.core.files.base import ContentFile
from recipes.models import Recipe
from ..models import Subscription
from .recipes import ShortRecipeSerializer

User = get_user_model()


class FoodgramUserSerializer(BaseUserSerializer):
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
        read_only_fields = fields

    def get_is_subscribed(self, author):
        request = self.context.get('request') 
        return bool(
            request
            and hasattr(request, 'user')
            and request.user.is_authenticated
            and Subscription.objects.filter(user=request.user, author=author).exists()
        )


class UserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except (TypeError, ValueError):
                recipes_limit = 10**10
        else:
            recipes_limit = 10**10

        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True, context={'request': request}).data 
    
class UserAvatarSerializer(serializers.ModelSerializer): 
    avatar = serializers.CharField(required=True) 
    class Meta: 
        model = User 
        fields = ("avatar",)  

    def validate_avatar(self, value): 
        try: 
            if not value.startswith("data:image/"): 
                raise serializers.ValidationError("Invalid image format") 
            format, imgstr = value.split(";base64,") 
            data = base64.b64decode(imgstr) 
            if len(data) > 5 * 1024 * 1024: 
                raise serializers.ValidationError("Image size should not exceed 5MB") 
            return value 
        except Exception: 
            raise serializers.ValidationError("Invalid image data") 

    def update(self, instance, validated_data): 
        format, imgstr = validated_data["avatar"].split(";base64,") 
        ext = format.split("/")[-1] 
        filename = f"avatar_{instance.id}.{ext}" 
        data = ContentFile(base64.b64decode(imgstr), name=filename) 
        instance.avatar.save(filename, data, save=True) 
        return instance
    