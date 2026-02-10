"""
Serializers for user authentication.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates password match and creates user with hashed password.
    Accepts 'type' field to set the user as 'customer' or 'business'.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    repeated_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'email': {'required': True},
            'type': {'required': False}
        }

    def validate(self, attrs):
        """
        Validate that both password fields match.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create new user with hashed password and user type.
        """
        validated_data.pop('repeated_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data.get('type', 'customer')
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Accepts username and password for authentication.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading and updating user profile.

    Excludes sensitive fields like password.
    """

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'type',
            'location',
            'tel',
            'description',
            'working_hours',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']