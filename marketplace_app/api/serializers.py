from rest_framework import serializers
from ..models import Offer, OfferDetail, Order, Review
from auth_app.api.serializers import UserSerializer
from django.contrib.auth.models import User

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Return a simple detail URL for the given `OfferDetail` instance.

        Parameters:
            obj (OfferDetail): The offer detail instance.

        Returns:
            str: A relative URL to the offer detail resource.
        """
        return f'/offerdetails/{obj.id}/'


class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    details = OfferDetailListSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']


class OfferDetailViewSerializer(serializers.ModelSerializer):
    """Serializer für GET /api/offers/{id}/ (Detail-Ansicht)"""
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    details = OfferDetailListSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """
        Validate the `details` nested list when creating/updating an `Offer`.

        Enforces that non-partial requests include exactly three detail objects
        with offer types 'basic', 'standard' and 'premium'. For partial updates
        this check is skipped.

        Parameters:
            value (list): List of detail dicts provided in the request.

        Returns:
            list: The validated `details` value.

        Raises:
            serializers.ValidationError: If the details list is invalid.
        """

        if not self.partial:
            if len(value) != 3:
                raise serializers.ValidationError("Ein Offer muss genau 3 Details enthalten (basic, standard, premium).")
        
            offer_types = [detail['offer_type'] for detail in value]
            required_types = {'basic', 'standard', 'premium'}
            if set(offer_types) != required_types:
                raise serializers.ValidationError("Die Details müssen die Typen 'basic', 'standard' und 'premium' enthalten.")
    
        return value

    def create(self, validated_data):
        """
        Create an `Offer` and its nested `OfferDetail` items.

        Parameters:
            validated_data (dict): Data validated by the serializer, must
                include a `details` list of detail dicts.

        Returns:
            Offer: The newly created `Offer` instance with persisted details.
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


    def update(self, instance, validated_data):
        """
        Update an `Offer` instance and optionally its nested `OfferDetail`s.

        Behavior:
            - Updates top-level `Offer` fields present in `validated_data`.
            - If `details` is provided, it updates existing details by
              `offer_type` or creates new `OfferDetail`s for missing types.

        Parameters:
            instance (Offer): The offer instance to update.
            validated_data (dict): Validated input data, may contain `details`.

        Returns:
            Offer: The updated `Offer` instance.
        """
        details_data = validated_data.pop('details', None)

        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()

        if details_data is not None:
            existing_details = {
                detail.offer_type: detail
                for detail in instance.details.all()
            }

            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')

                if offer_type in existing_details:

                    detail = existing_details[offer_type]
                    detail.title = detail_data.get('title', detail.title)
                    detail.revisions = detail_data.get(
                        'revisions', detail.revisions)
                    detail.delivery_time_in_days = detail_data.get(
                        'delivery_time_in_days', detail.delivery_time_in_days)
                    detail.price = detail_data.get('price', detail.price)
                    detail.features = detail_data.get('features', detail.features)
                    detail.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)

        return instance


class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(source='buyer', read_only=True)
    business_user = serializers.SerializerMethodField()
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(), 
        write_only=True, 
        source='offer_detail'
    )
    
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'customer_user', 
            'business_user', 
            'title', 
            'revisions', 
            'delivery_time_in_days', 
            'price', 
            'features', 
            'offer_type', 
            'status', 
            'created_at',
            'updated_at',
            'offer_detail_id'
        ]

    def get_business_user(self, obj):
        """
        SerializerMethodField returning the business (owner) user id for an order.

        Parameters:
            obj (Order): Order instance being serialized.

        Returns:
            int: Primary key of the business user who owns the related offer.
        """
        return obj.offer_detail.offer.owner.id


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """
        Ensure rating is within the allowed range (1-5).

        Parameters:
            value (int): Candidate rating value.

        Returns:
            int: The validated rating value.

        Raises:
            serializers.ValidationError: If rating is outside 1-5.
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating muss zwischen 1 und 5 liegen.")
        return value
    
    def validate_business_user(self, value):
        """
        Validate that the provided `business_user` corresponds to a profile
        with type 'business'.

        Parameters:
            value (User): Candidate business user instance.

        Returns:
            User: The validated user.

        Raises:
            serializers.ValidationError: If the user has no profile or is not a business.
        """
        try:
            if value.profile.type != 'business':
                raise serializers.ValidationError("Bewertungen können nur für Business-Nutzer erstellt werden.")
        except:
            raise serializers.ValidationError("Der angegebene Benutzer hat kein gültiges Profil.")
        return value