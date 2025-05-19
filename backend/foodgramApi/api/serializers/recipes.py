from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeIngredient, Ingredient
from .users import FoodgramUserSerializer
import base64
from django.core.files.base import ContentFile
from django.db import transaction
from ..models import Favorite, ShoppingCart

User = get_user_model()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients.all')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields
        
    def get_is_favorited(self, recipe):
        request = self.context.get("request") 
        return bool(
            request
            and hasattr(request, 'user')
            and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists()
        return False


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, required=True)
    image = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ("ingredients", "image", "name", "text", "cooking_time")

    def validate_ingredients(self, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError("Ingredients list cannot be empty.")

        ingredient_ids = [item["id"] for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ingredients must be unique within a recipe. Duplicate IDs found.")

        return ingredients_data

    def validate(self, data):
        if self.instance and "ingredients" not in data:
            raise serializers.ValidationError({"ingredients": "This field is required"})
        return data

    def validate_image(self, value):
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

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        image_data = validated_data.pop("image")

        validated_data["author"] = self.context["request"].user
        recipe = super().create(validated_data)

        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        filename = f"recipe_{recipe.id}.{ext}"
        data = ContentFile(base64.b64decode(imgstr), name=filename)
        recipe.image.save(filename, data, save=True)

        self._bulk_create_recipe_ingredients(recipe, ingredients_data)

        return recipe

    def _bulk_create_recipe_ingredients(self, recipe, ingredients_data):
        recipe_ingredients_to_create = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients_to_create)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._bulk_create_recipe_ingredients(instance, ingredients_data)

        image_base64_data = validated_data.pop("image", None)

        if image_base64_data:
            format_str, imgstr = image_base64_data.split(";base64,")
            ext = format_str.split("/")[-1]
            filename = f"recipe_{instance.id}.{ext}"
            decoded_image_data = ContentFile(base64.b64decode(imgstr), name=filename)
            instance.image.save(filename, decoded_image_data, save=True)

        return super().update(instance, validated_data)


    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields
