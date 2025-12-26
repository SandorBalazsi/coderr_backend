
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Min
from rest_framework.views import APIView
from django.contrib.auth.models import User

from ..models import Offer, OfferDetail, Order, Review
from .serializers import OfferDetailSerializer, OfferDetailViewSerializer, OfferSerializer, OfferListSerializer, OrderSerializer, ReviewSerializer



class OfferPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    pagination_class = OfferPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferSerializer


    def get_queryset(self):
        queryset = Offer.objects.all()
    
        creator_id = self.request.query_params.get('creator_id', None)
        if creator_id:
            queryset = queryset.filter(owner_id=creator_id)
    
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.annotate(
                    lowest_price=Min('details__price')
                ).filter(lowest_price__gte=min_price)
            except ValueError:
                pass
    
        max_delivery_time = self.request.query_params.get('max_delivery_time', None)
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                queryset = queryset.annotate(
                    fastest_delivery=Min('details__delivery_time_in_days')
                ).filter(fastest_delivery__lte=max_delivery_time)
            except ValueError:
                pass
    
        ordering = self.request.query_params.get('ordering', None)
        if ordering == 'min_price':
            queryset = queryset.annotate(
                lowest_price=Min('details__price')
            ).order_by('lowest_price')
        elif ordering == '-min_price':
            queryset = queryset.annotate(
                lowest_price=Min('details__price')
            ).order_by('-lowest_price')
        elif ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')
    
        return queryset.select_related('owner').prefetch_related('details')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

class OrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            profile = business_user.profile
            if profile.type != 'business':
                return Response(
                    {'detail': 'Der angegebene Benutzer ist kein Geschäftsnutzer.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'detail': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        count = Order.objects.filter(
            buyer_id=business_user_id,
            status='in_progress'
        ).count()
        
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            profile = business_user.profile
            if profile.type != 'business':
                return Response(
                    {'detail': 'Der angegebene Benutzer ist kein Geschäftsnutzer.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'detail': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        count = Order.objects.filter(
            buyer_id=business_user_id,
            status='completed'
        ).count()
        
        return Response({'completed_order_count': count})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)