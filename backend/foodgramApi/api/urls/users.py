from django.urls import path
from .views import (
    user_avatar,
    subscriptions,
    subscribe,
)

urlpatterns = [
    path('me/avatar/', user_avatar, name='user-avatar'),
    path('subscriptions/', subscriptions, name='user-subscriptions'),
    path('<int:id>/subscribe/', subscribe, name='user-subscribe'),
]
