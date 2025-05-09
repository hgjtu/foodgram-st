from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Recipe, RecipeIngredient, Ingredient
from users.serializers import UserSerializer
import base64
from django.core.files.base import ContentFile

User = get_user_model()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers\
        .ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True)
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

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.in_shopping_carts.filter(id=request.user.id).exists()
        return False


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, required=True)
    image = serializers.CharField(required=True)

    class Meta:
        model = Recipe
        fields = ("ingredients", "image", "name", "text", "cooking_time")

    def validate_ingredients(self, value):
        if not value:
            raise serializers\
                .ValidationError("Ingredients list cannot be empty")

        ingredient_ids = [item["id"] for item in value]
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            raise serializers\
                .ValidationError("One or more ingredients do not exist")

        return value

    def validate(self, data):
        if self.instance and "ingredients" not in data:
            raise serializers\
                .ValidationError({"ingredients": "This field is required"})
        return data

    def validate_image(self, value):
        try:
            if not value.startswith("data:image/"):
                raise serializers\
                    .ValidationError("Invalid image format")

            format, imgstr = value.split(";base64,")

            data = base64.b64decode(imgstr)

            if len(data) > 5 * 1024 * 1024:
                raise serializers\
                    .ValidationError("Image size should not exceed 5MB")

            return value
        except Exception:
            raise serializers.ValidationError("Invalid image data")

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        image_data = validated_data.pop("image")

        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )

        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        filename = f"recipe_{recipe.id}.{ext}"
        data = ContentFile(base64.b64decode(imgstr), name=filename)
        recipe.image.save(filename, data, save=True)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )

        return recipe

    def update(self, instance, validated_data):
        if "ingredients" in validated_data:
            ingredients_data = validated_data.pop("ingredients")
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient_id=ingredient_data["id"],
                    defaults={"amount": ingredient_data["amount"]},
                )

        if "image" in validated_data:
            image_data = validated_data.pop("image")
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            filename = f"recipe_{instance.id}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)
            instance.image.save(filename, data, save=True)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
