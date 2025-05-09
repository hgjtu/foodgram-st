from django.urls import path
from .views import ingredient_list, ingredient_detail
from rest_framework.response import Response
from rest_framework import status


def method_not_allowed(request, *args, **kwargs):
    return Response(
        {"detail": "Method not allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


urlpatterns = [
    path("", ingredient_list, name="ingredient-list"),
    path("<int:id>/", ingredient_detail, name="ingredient-detail"),
]
