from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeIngredient, Ingredient
from .users import FoodgramUserSerializer
import base64
from django.core.files.base import ContentFile
from django.db import transaction

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
    ingredients = RecipeIngredientSerializer(many=True, source='recipeingredient_set')
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

    def get_is_favorited(self, recipe):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return recipe.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return recipe.in_shopping_carts.filter(id=request.user.id).exists()
        return False


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ingredient with this ID does not exist.")
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, required=True)
    image = serializers.CharField(required=True)

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
        recipe_ingredients_to_create = []
        for ingredient_data in ingredients_data:
            recipe_ingredients_to_create.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients_to_create)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._bulk_create_recipe_ingredients(instance, ingredients_data)

        image_base64_data = validated_data.pop("image", None)
        instance = super().update(instance, validated_data)

        if image_base64_data:
            format_str, imgstr = image_base64_data.split(";base64,")
            ext = format_str.split("/")[-1]
            filename = f"recipe_{instance.id}.{ext}"
            decoded_image_data = ContentFile(base64.b64decode(imgstr), name=filename)
            instance.image.save(filename, decoded_image_data, save=True)

        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class RecipeGetShortLinkSerializer(serializers.Serializer):
    short_link = serializers.URLField(source="short-link")

    class Meta:
        fields = ("short_link",) 