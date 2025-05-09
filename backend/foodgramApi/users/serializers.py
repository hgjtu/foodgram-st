from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import base64
from django.core.files.base import ContentFile
from .models import User
from recipes.models import Recipe


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


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
                raise serializers\
                    .ValidationError("Image size should not exceed 5MB")

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


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует."
            )
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None


class UserWithRecipesSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False

    def get_recipes(self, obj):
        from recipes.serializers import ShortRecipeSerializer

        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except (TypeError, ValueError):
                recipes_limit = 3
        else:
            recipes_limit = 3

        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        return ShortRecipeSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None
