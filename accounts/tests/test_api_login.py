"""
Tests for the login API endpoint.
POST /api/login/
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class LoginAPITest(APITestCase):
    """
    Tests for POST /api/login/
    """

    def setUp(self):
        """
        Create a test user and set up client.
        """
        self.client = APIClient()
        self.url = '/api/login/'
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='TestPass123!'
        )

    def test_login_success(self):
        """
        Test successful login returns token and 200.
        """
        data = {
            'username': 'loginuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'loginuser')

    def test_login_wrong_password(self):
        """
        Test login fails with incorrect password.
        """
        data = {
            'username': 'loginuser',
            'password': 'WrongPass!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_login_nonexistent_user(self):
        """
        Test login fails with a username that does not exist.
        """
        data = {
            'username': 'ghostuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_username(self):
        """
        Test login fails when username field is missing.
        """
        data = {
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """
        Test login fails when password field is missing.
        """
        data = {
            'username': 'loginuser'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_body(self):
        """
        Test login fails with empty request body.
        """
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)