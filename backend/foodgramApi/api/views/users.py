from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from ..models import Subscription
from ..serializers.users import (
    UserWithRecipesSerializer,
    FoodgramUserSerializer,
    UserAvatarSerializer
)
from djoser.views import UserViewSet as DjoserUserViewSet
from .recipes import RecipePagination

User = get_user_model()


class UserActionsViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['put', 'delete'], permission_classes=[IsAuthenticated])
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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscribed_author_ids = Subscription.objects.filter(user=user).values_list('author_id', flat=True)
        authors_user_is_subscribed_to = User.objects.filter(id__in=subscribed_author_ids)

        paginator = RecipePagination()
        result_page = paginator.paginate_queryset(authors_user_is_subscribed_to, request)
        serializer = UserWithRecipesSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author_to_subscribe_to = get_object_or_404(User, id=id)
        current_user = request.user

        if author_to_subscribe_to == current_user:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            if Subscription.objects.filter(user=current_user, author=author_to_subscribe_to).exists():
                return Response(
                    {"errors": f"Вы уже подписаны на пользователя {author_to_subscribe_to.username}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=current_user, author=author_to_subscribe_to)
            serializer = UserWithRecipesSerializer(author_to_subscribe_to, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            subscription_entry = Subscription.objects.filter(user=current_user, author=author_to_subscribe_to)
            if not subscription_entry.exists():
                return Response(
                    {"errors": f"Вы не были подписаны на пользователя {author_to_subscribe_to.username}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
