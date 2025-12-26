
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django.db.models import Min

from ..models import Offer, Order, Review
from .serializers import OfferSerializer, OrderSerializer, ReviewSerializer
from .list_serializers import OfferListSerializer


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



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)