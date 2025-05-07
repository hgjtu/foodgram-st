from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserAvatarSerializer,
    PasswordChangeSerializer
)

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    paginator = CustomPagination()
    users = User.objects.all()
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_create(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, id):
    user = get_object_or_404(User, id=id)
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_avatar(request):
    if request.method == 'DELETE':
        if request.user.avatar:
            if request.user.avatar.name != 'users/image.png':
                default_storage.delete(request.user.avatar.path)
            request.user.avatar = 'users/image.png'
            request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    serializer = UserAvatarSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({'avatar': request.build_absolute_uri(user.avatar.url)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_set_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
