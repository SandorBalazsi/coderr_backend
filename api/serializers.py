from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Offer, Order, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class OfferSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'price', 'owner', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)
    offer_id = serializers.PrimaryKeyRelatedField(queryset=Offer.objects.all(), write_only=True, source='offer')

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'offer', 'offer_id', 'status', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'offer', 'rating', 'comment', 'created_at']
