from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_auth_views

from . import views

router = DefaultRouter()
router.register(r'offers', views.OfferViewSet, basename='offer')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', drf_auth_views.obtain_auth_token, name='login'),
]
