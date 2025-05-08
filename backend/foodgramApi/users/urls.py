from django.urls import path
from .views import (
    user_list,
    user_create,
    user_detail,
    user_me,
    user_avatar,
    user_set_password,
    subscriptions,
    subscribe,
    unsubscribe
)

urlpatterns = [
    path('', user_list, name='user-list'),
    path('', user_create, name='user-create'),
    path('<int:id>/', user_detail, name='user-detail'),
    path('me/', user_me, name='user-me'),
    path('me/avatar/', user_avatar, name='user-avatar'),
    path('set_password/', user_set_password, name='user-set-password'),
    path('subscriptions/', subscriptions, name='user-subscriptions'),
    path('<int:id>/subscribe/', subscribe, name='user-subscribe'),
    path('<int:id>/subscribe/', unsubscribe, name='user-unsubscribe'),
] 