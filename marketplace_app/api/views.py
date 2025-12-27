
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from django.db.models import Min
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Avg
from auth_app.models import UserProfile
from marketplace_app.api.permissions import IsBusinessUser, IsCustomerUser, IsOrderOwner, IsReviewOwner

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
        """
        Select the appropriate serializer class depending on the action.

        Returns:
            Serializer class: `OfferListSerializer` for list, `OfferDetailViewSerializer`
            for retrieve, otherwise `OfferSerializer` for create/update operations.
        """
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferSerializer


    def get_queryset(self):
        """
        Return a queryset of `Offer` objects filtered and ordered according to
        query parameters.

        Supported query params:
            - `creator_id`: filters offers by owner id.
            - `min_price`: include offers whose lowest detail price >= value.
            - `max_delivery_time`: include offers whose fastest delivery <= value.
            - `ordering`: supports 'min_price' and '-min_price' (uses annotated values)
              as well as normal model field ordering.

        Returns:
            QuerySet: The filtered/ordered queryset with `owner` selected and
            `details` prefetched for performance.
        """
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
        """
        Save a new `Offer` instance setting the `owner` to the requesting user.

        Parameters:
            serializer: The serializer instance with validated data.
        """
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Return permission instances depending on the action.

        - Authenticated users are required for create/update/destroy operations.
        - Read-only actions allow unauthenticated access.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related(
        'buyer', 
        'offer_detail__offer__owner'
    ).order_by('-created_at')
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Return permission instances for `OrderViewSet` based on action.

        - `create`: authenticated users only.
        - `update`/`partial_update`: authenticated business users who own the order.
        - `destroy`: admin users only.
        - others: read-only access allowed.
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsBusinessUser(), IsOrderOwner()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        """
        Persist a new `Order` setting the `buyer` to the requesting user.

        Parameters:
            serializer: The serializer instance with validated data.
        """
        serializer.save(buyer=self.request.user)

class OrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, business_user_id):
        """
        Return the number of in-progress orders for a given business user id.

        Parameters:
            request: DRF request object.
            business_user_id (int): Primary key of the business user.

        Returns:
            Response: JSON response with `order_count` or 404 if user/profile invalid.
        """
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
        """
        Return the number of completed orders for a given business user id.

        See `OrderCountView.get` for behavior; this filters `status='completed'.`
        """
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
    queryset = Review.objects.all().select_related('business_user', 'reviewer').order_by('-created_at')
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    
    def get_permissions(self):
        """
        Return permission instances for `ReviewViewSet` actions.

        - `create`: must be an authenticated customer user.
        - update/partial_update/destroy: must be the review owner.
        - otherwise: read-only access allowed.
        """
        if self.action == 'create':
            # Nur Customer-User dürfen Reviews erstellen
            return [permissions.IsAuthenticated(), IsCustomerUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Nur der Ersteller darf seine Review bearbeiten/löschen
            return [permissions.IsAuthenticated(), IsReviewOwner()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        """
        Optionally filter reviews by `business_user_id` or `reviewer_id`
        query parameters.

        Returns:
            QuerySet: Filtered review queryset.
        """
        queryset = super().get_queryset()

        business_user_id = self.request.query_params.get('business_user_id', None)
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        
        reviewer_id = self.request.query_params.get('reviewer_id', None)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Save a new `Review` setting the `reviewer` to the requesting user.
        """
        serializer.save(reviewer=self.request.user)

class BaseInfoView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Return summary base information used by the frontend dashboard.

        Provides counts for reviews, average rating, number of business profiles,
        and total offers.

        Returns:
            Response: JSON object with aggregated values.
        """
        review_count = Review.objects.count()
        
        avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(avg_rating, 1) if avg_rating else 0.0
        
        business_profile_count = UserProfile.objects.filter(type='business').count()
        
        # Anzahl Offers
        offer_count = Offer.objects.count()
        
        return Response({
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        })