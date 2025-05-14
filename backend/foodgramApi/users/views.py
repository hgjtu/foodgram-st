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
    PasswordChangeSerializer,
    UserWithRecipesSerializer,
)

User = get_user_model()


class ExtendedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def user_list(request):
    if request.method == "POST":
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    users = User.objects.all()
    paginator = ExtendedPagination()
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(result_page,
                                many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_detail(request, id):
    user = get_object_or_404(User, id=id)
    serializer = UserSerializer(user, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_me(request):
    serializer = UserSerializer(request.user, context={"request": request})
    return Response(serializer.data)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_avatar(request):
    if request.method == "DELETE":
        if request.user.avatar:
            if request.user.avatar.name != "users/image.png":
                default_storage.delete(request.user.avatar.path)
            request.user.avatar = None
            request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = UserAvatarSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"avatar": request.build_absolute_uri(user.avatar.url)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_set_password(request):
    serializer = PasswordChangeSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    subscribed_users = User.objects.filter(subscribers=request.user)

    paginator = ExtendedPagination()
    result_page = paginator.paginate_queryset(subscribed_users, request)

    serializer = UserWithRecipesSerializer(
        result_page, many=True, context={"request": request}
    )

    return paginator.get_paginated_response(serializer.data)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def subscribe(request, id):
    author = get_object_or_404(User, id=id)

    if request.method == "POST":
        if author == request.user:
            return Response(
                {"detail": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if author.subscribers.filter(id=request.user.id).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author.subscribers.add(request.user)

        serializer = UserWithRecipesSerializer(author,
                                               context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        if not author.subscribers.filter(id=request.user.id).exists():
            return Response(
                {"detail": "Вы не были подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author.subscribers.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
