from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('', include('api.urls.ingredients')),
    path('', include('api.urls.recipes')),
    path('', include('api.urls.users')),
    path('s/', include('api.urls.shortlinks')), # ЧТО-ТО сделать
] 