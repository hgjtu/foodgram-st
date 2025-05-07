from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import base64
from django.core.files.base import ContentFile
from .models import User

User = get_user_model()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        try:
            # Check if the string is a valid base64 image
            if not value.startswith('data:image/'):
                raise serializers.ValidationError('Invalid image format')
            
            # Split the string to get the image data
            format, imgstr = value.split(';base64,')
            ext = format.split('/')[-1]
            
            # Try to decode the base64 string
            data = base64.b64decode(imgstr)
            
            # Validate file size (max 5MB)
            if len(data) > 5 * 1024 * 1024:
                raise serializers.ValidationError('Image size should not exceed 5MB')
            
            return value
        except Exception as e:
            raise serializers.ValidationError('Invalid image data')

    def update(self, instance, validated_data):
        # Split the string to get the image data
        format, imgstr = validated_data['avatar'].split(';base64,')
        ext = format.split('/')[-1]
        
        # Generate filename
        filename = f'avatar_{instance.id}.{ext}'
        
        # Create file from base64 data
        data = ContentFile(base64.b64decode(imgstr), name=filename)
        
        # Save the file
        instance.avatar.save(filename, data, save=True)
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        read_only_fields = ('id',)

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
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None 