from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                {"non_field_errors": ["Необходимо указать email и пароль."]}
            )

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise serializers.ValidationError(
                    {"non_field_errors": ["Неверный email или пароль."]}
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Неверный email или пароль."]}
            )

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return {"auth_token": token.key}
