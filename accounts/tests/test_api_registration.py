"""
Tests for the registration API endpoint.
POST /api/registration/
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationAPITest(APITestCase):
    """
    Tests for POST /api/registration/
    """

    def setUp(self):
        """
        Set up API client and endpoint URL.
        """
        self.client = APIClient()
        self.url = '/api/registration/'

    def test_registration_success(self):
        """
        Test successful registration returns token and 201.
        """
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!',
            'type': 'customer'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'new@example.com')

    def test_registration_as_business(self):
        """
        Test successful registration with type 'business'.
        """
        data = {
            'username': 'newbiz',
            'email': 'biz@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!',
            'type': 'business'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify type wurde korrekt gespeichert
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(username='newbiz')
        self.assertEqual(user.type, 'business')

    def test_registration_password_mismatch(self):
        """
        Test registration fails when passwords do not match.
        """
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'DifferentPass!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_email(self):
        """
        Test registration fails when email is missing.
        """
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_username(self):
        """
        Test registration fails when username is missing.
        """
        data = {
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        """
        Test registration fails when username already exists.
        """
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPass123!'
        )

        data = {
            'username': 'existinguser',
            'email': 'other@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_creates_token_in_db(self):
        """
        Test that registration creates a token entry in the database.
        """
        data = {
            'username': 'tokenuser',
            'email': 'token@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        user = User.objects.get(username='tokenuser')
        token = Token.objects.get(user=user)

        self.assertEqual(response.data['token'], token.key)

    def test_registration_weak_password(self):
        """
        Test registration fails with a weak/too short password.
        """
        data = {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': '123',
            'repeated_password': '123'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)