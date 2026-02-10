"""
Permission tests for accounts app.
Ensures only the right users can access or modify resources.
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class AccountsPermissionTest(APITestCase):
    """
    Tests that registration and login are public,
    and profiles require authentication.
    """

    def setUp(self):
        """
        Create two users with tokens.
        """
        self.client = APIClient()

        self.user_a = User.objects.create_user(
            username='usera',
            email='a@example.com',
            password='TestPass123!',
            type='business'
        )
        self.token_a = Token.objects.create(user=self.user_a)

        self.user_b = User.objects.create_user(
            username='userb',
            email='b@example.com',
            password='TestPass123!',
            type='customer'
        )
        self.token_b = Token.objects.create(user=self.user_b)

    def test_registration_no_auth_needed(self):
        """
        POST /api/registration/ is public - no token required.
        """
        data = {
            'username': 'newperson',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'repeated_password': 'TestPass123!'
        }
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_no_auth_needed(self):
        """
        POST /api/login/ is public - no token required.
        """
        data = {
            'username': 'usera',
            'password': 'TestPass123!'
        }
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_requires_auth(self):
        """
        GET /api/profile/<id>/ returns 401 without token.
        """
        response = self.client.get(f'/api/profile/{self.user_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_requires_auth(self):
        """
        PATCH /api/profile/<id>/ returns 401 without token.
        """
        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_b_cannot_update_user_a_profile(self):
        """
        User B cannot update User A's profile - returns 403.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)

        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/',
            {'location': 'Munich'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_a_can_update_own_profile(self):
        """
        User A can update their own profile - returns 200.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_a.key)

        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/',
            {'location': 'Hamburg'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_list_requires_auth(self):
        """
        GET /api/profiles/business/ returns 401 without token.
        """
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_list_requires_auth(self):
        """
        GET /api/profiles/customer/ returns 401 without token.
        """
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)