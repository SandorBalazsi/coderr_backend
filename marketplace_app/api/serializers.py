from rest_framework import serializers
from ..models import Offer, OfferDetail, Order, Review
from auth_app.api.serializers import UserSerializer


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

        if not self.partial:
            if len(value) != 3:
                raise serializers.ValidationError("Ein Offer muss genau 3 Details enthalten (basic, standard, premium).")
        
            offer_types = [detail['offer_type'] for detail in value]
            required_types = {'basic', 'standard', 'premium'}
            if set(offer_types) != required_types:
                raise serializers.ValidationError("Die Details müssen die Typen 'basic', 'standard' und 'premium' enthalten.")
    
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


    def update(self, instance, validated_data):
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
    buyer = UserSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)
    offer_id = serializers.PrimaryKeyRelatedField(
        queryset=Offer.objects.all(), write_only=True, source='offer')

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'offer', 'offer_id', 'status', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'offer', 'rating', 'comment', 'created_at']
