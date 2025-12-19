from rest_framework import serializers
from ..models import Offer


class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]

    def get_user(self, obj):
        return obj.owner.id if obj.owner else None

    def get_image(self, obj):
        return None

    def get_updated_at(self, obj):
        return None

    def get_details(self, obj):
        return []

    def get_min_price(self, obj):
        try:
            return int(obj.price)
        except Exception:
            return None

    def get_min_delivery_time(self, obj):
        return 7

    def get_user_details(self, obj):
        owner = obj.owner
        if not owner:
            return None
        return {
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'username': owner.username,
        }
