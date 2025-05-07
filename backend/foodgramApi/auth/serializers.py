from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise serializers.ValidationError('Неверный email или пароль')
            except User.DoesNotExist:
                raise serializers.ValidationError('Неверный email или пароль')
        else:
            raise serializers.ValidationError('Необходимо указать email и пароль')

        return data

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        token, _ = Token.objects.get_or_create(user=user)
        return {'auth_token': token.key}

