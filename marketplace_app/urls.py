from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_auth_views

from .api import views

router = DefaultRouter()
router.register(r'offers', views.OfferViewSet, basename='offer')
router.register(r'offerdetails', views.OfferDetailViewSet, basename='offerdetail')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.ReviewViewSet, basename='review')


urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:business_user_id>/', views.OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', views.CompletedOrderCountView.as_view(), name='completed-order-count'),
]
