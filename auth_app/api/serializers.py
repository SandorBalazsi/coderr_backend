from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=['customer', 'business'],
        write_only=True,
        required=False,
        default='customer'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
    
    def validate_username(self, value):

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({
                "repeated_password": "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type', 'customer')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        return user