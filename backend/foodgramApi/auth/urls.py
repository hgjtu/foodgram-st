from django.urls import path
from .views import token_login, token_logout

urlpatterns = [
    path("token/login/", token_login, name="token_login"),
    path("token/logout/", token_logout, name="token_logout"),
]
