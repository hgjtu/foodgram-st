from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .serializers import (
    CustomUserSerializer,
    UserAvatarSerializer,
    UserWithRecipesSerializer,
)

User = get_user_model()


class ExtendedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


class UserActionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        serializer = CustomUserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], permission_classes=[IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == "DELETE":
            if user.avatar:
                if hasattr(user.avatar, 'path') and user.avatar.name != "users/image.png":
                    default_storage.delete(user.avatar.path)
                elif user.avatar.name != "users/image.png":
                    user.avatar.delete(save=False)
                user.avatar = None
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserAvatarSerializer(user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        avatar_url = request.build_absolute_uri(updated_user.avatar.url) if updated_user.avatar else None
        return Response({'avatar': avatar_url})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='subscriptions')
    def list_subscriptions(self, request):
        user = request.user
        subscribed_to_users = User.objects.filter(subscribers=user)

        paginator = ExtendedPagination()
        result_page = paginator.paginate_queryset(subscribed_to_users, request)
        serializer = UserWithRecipesSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author_to_subscribe_to = get_object_or_404(User, id=pk)
        user = request.user

        if request.method == "POST":
            if author_to_subscribe_to == user:
                return Response(
                    {"errors": "Нельзя подписаться на самого себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if author_to_subscribe_to.subscribers.filter(id=user.id).exists():
                return Response(
                    {"errors": f"Вы уже подписаны на пользователя {author_to_subscribe_to.username}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            author_to_subscribe_to.subscribers.add(user)
            serializer = UserWithRecipesSerializer(author_to_subscribe_to, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            if not author_to_subscribe_to.subscribers.filter(id=user.id).exists():
                return Response(
                    {"errors": f"Вы не были подписаны на пользователя {author_to_subscribe_to.username}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            subscription_to_delete = get_object_or_404(
                User.subscriptions.through,
                from_user=user,
                to_user=author_to_subscribe_to
            )
            subscription_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
