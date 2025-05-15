from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.shortlinks import ShortLinkRecipeViewSet

router = DefaultRouter()
# Registering at the root of this router, path will be determined by include in v1.py
router.register(r'', ShortLinkRecipeViewSet, basename='public-recipe')

urlpatterns = [
    path('', include(router.urls)),
] 