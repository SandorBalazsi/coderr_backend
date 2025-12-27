from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration that also creates a `UserProfile`.

    Expects `repeated_password` and `type` (customer/business) on input. The
    `create` method will create both `User` and `UserProfile` records.
    """
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate(self, data):
        """
        Ensure the provided `password` and `repeated_password` match.

        Parameters:
            data (dict): Full input data for the serializer.

        Returns:
            dict: The validated data unchanged when passwords match.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        """
        Create a `User` and corresponding `UserProfile` using provided data.

        Parameters:
            validated_data (dict): Validated serializer data containing
                `username`, `email`, `password`, `repeated_password`, and `type`.

        Returns:
            User: The created `User` instance.
        """

        repeated_password = validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')

        user = User.objects.create_user(**validated_data)
        
        UserProfile.objects.create(user=user, type=user_type)
        
        return user



class RegisterSerializer(serializers.ModelSerializer):
    """
    Lightweight registration serializer used by alternative registration
    endpoints. Performs uniqueness checks and basic password confirmation.
    """
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
        """
        Ensure the username is not already taken.

        Parameters:
            value (str): Candidate username.

        Returns:
            str: The validated username.

        Raises:
            serializers.ValidationError: If username already exists.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """
        Ensure the email address is unique when provided.

        Parameters:
            value (str): Candidate email.

        Returns:
            str: The validated email.

        Raises:
            serializers.ValidationError: If email already exists.
        """
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """
        Cross-field validation to confirm matching passwords.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({
                "repeated_password": "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new `User` from validated registration data.

        The `repeated_password` is discarded; `type` may be present but is not
        used by this serializer to create a `UserProfile`.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type', 'customer')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the `UserProfile` model that allows updating profile fields
    and related `User` name fields via nested `user` data.
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at'
        ]
        read_only_fields = ['user', 'username', 'email', 'created_at']
    
    def update(self, instance, validated_data):
        """
        Handle updates to both `UserProfile` and the linked `User` model.

        Parameters:
            instance (UserProfile): Profile instance to update.
            validated_data (dict): Data validated by the serializer; may contain
                a nested `user` dict with `first_name` and `last_name`.

        Returns:
            UserProfile: The updated profile instance.
        """

        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
    def to_representation(self, instance):
        """
        Ensure certain fields serialize as empty strings instead of null
        values for more consistent API responses.
        """
        data = super().to_representation(instance)
        
        fields_to_check = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        
        for field in fields_to_check:
            if data.get(field) is None:
                data[field] = ''
        
        return data
    
class CustomerProfileSerializer(serializers.ModelSerializer):
    """Simplified serializer for customer profiles - fewer fields"""
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'type'
        ]
    
    def to_representation(self, instance):
        """Ensure empty strings instead of null values"""
        data = super().to_representation(instance)
        
        fields_to_check = ['first_name', 'last_name']
        
        for field in fields_to_check:
            if data.get(field) is None:
                data[field] = ''
        
        return data