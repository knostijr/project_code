"""
Views for user authentication.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model

from .serializers import (
    RegistrationSerializer,
    LoginSerializer
)

User = get_user_model()


class RegistrationView(APIView):
    """
    API view for user registration.

    POST /api/registration/
    Creates a new user and returns an authentication token.
    No permissions required.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request for user registration.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user login.

    POST /api/login/
    Authenticates user and returns token.
    No permissions required.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request for user login.
        """
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_200_OK)

            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)