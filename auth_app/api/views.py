from django.contrib.auth.models import User
from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import UserSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(ObtainAuthToken):

    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )