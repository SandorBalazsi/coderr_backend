from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import views

router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/business/', views.UserProfileViewSet.as_view({'get': 'business_profiles'}), name='business-profiles'),
    path('profiles/customer/', views.UserProfileViewSet.as_view({'get': 'customer_profiles'}), name='customer-profiles'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
] 