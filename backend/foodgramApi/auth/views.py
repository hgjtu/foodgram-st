from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import TokenSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def token_login(request):
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.save(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_logout(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_204_NO_CONTENT)
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)