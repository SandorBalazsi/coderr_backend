from django.contrib.auth.models import User
from rest_framework import status, generics, permissions, serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from auth_app.models import UserProfile
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer, CustomerProfileSerializer
from .permissions import IsOwnProfile


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
    
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


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
        

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user__id'
    lookup_url_kwarg = 'pk'
    
    def get_permissions(self):

        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnProfile()]
        elif self.action in ['business_profiles', 'customer_profiles']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @action(detail=False, methods=['get'], url_path='business')
    def business_profiles(self, request):

        profiles = UserProfile.objects.filter(type='business')
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='customer')
    def customer_profiles(self, request):

        profiles = UserProfile.objects.filter(type='customer')
        serializer = CustomerProfileSerializer(profiles, many=True)
        return Response(serializer.data)