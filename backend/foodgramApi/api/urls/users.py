from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.users import UserActionsViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserActionsViewSet, basename='user-actions')

urlpatterns = [
    path('', include(router.urls)),
] 