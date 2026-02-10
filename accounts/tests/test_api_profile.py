"""
Tests for the profile API endpoints.
GET    /api/profile/<pk>/
PATCH  /api/profile/<pk>/
GET    /api/profiles/business/
GET    /api/profiles/customer/
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class ProfileRetrieveAPITest(APITestCase):
    """
    Tests for GET /api/profile/<pk>/
    """

    def setUp(self):
        """
        Create a test user and authenticate.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='TestPass123!',
            type='business'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_profile_success(self):
        """
        Test retrieving own profile returns 200 with correct data.
        """
        url = f'/api/profile/{self.user.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['type'], 'business')

    def test_get_profile_unauthorized(self):
        """
        Test retrieving a profile without token returns 401.
        """
        self.client.credentials()  # Token entfernen
        url = f'/api/profile/{self.user.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        """
        Test retrieving a non-existent profile returns 404.
        """
        url = '/api/profile/9999/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileUpdateAPITest(APITestCase):
    """
    Tests for PATCH /api/profile/<pk>/
    """

    def setUp(self):
        """
        Create two users - one authenticated, one as 'other'.
        """
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='TestPass123!',
            type='business'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!',
            type='customer'
        )

    def test_update_own_profile_location(self):
        """
        Test updating own profile location returns 200.
        """
        url = f'/api/profile/{self.user.id}/'
        data = {'location': 'Berlin'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_update_own_profile_multiple_fields(self):
        """
        Test updating multiple profile fields at once.
        """
        url = f'/api/profile/{self.user.id}/'
        data = {
            'location': 'Munich',
            'tel': '0491234567',
            'description': 'Senior Developer',
            'working_hours': 35
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Munich')
        self.assertEqual(response.data['tel'], '0491234567')
        self.assertEqual(response.data['description'], 'Senior Developer')
        self.assertEqual(response.data['working_hours'], 35)

    def test_update_other_profile_forbidden(self):
        """
        Test that updating another user's profile returns 403.
        """
        url = f'/api/profile/{self.other_user.id}/'
        data = {'location': 'Hamburg'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_unauthorized(self):
        """
        Test that updating without token returns 401.
        """
        self.client.credentials()
        url = f'/api/profile/{self.user.id}/'
        data = {'location': 'Berlin'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileListAPITest(APITestCase):
    """
    Tests for GET /api/profiles/business/ and GET /api/profiles/customer/
    """

    def setUp(self):
        """
        Create business and customer users, authenticate.
        """
        self.client = APIClient()

        self.business_user = User.objects.create_user(
            username='bizuser',
            email='biz@example.com',
            password='TestPass123!',
            type='business'
        )
        self.customer_user = User.objects.create_user(
            username='custuser',
            email='cust@example.com',
            password='TestPass123!',
            type='customer'
        )

        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_list_business_profiles(self):
        """
        Test that only business users are returned.
        """
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        self.assertIn('bizuser', usernames)
        self.assertNotIn('custuser', usernames)

    def test_list_customer_profiles(self):
        """
        Test that only customer users are returned.
        """
        response = self.client.get('/api/profiles/customer/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        self.assertIn('custuser', usernames)
        self.assertNotIn('bizuser', usernames)

    def test_list_business_unauthorized(self):
        """
        Test listing business profiles without token returns 401.
        """
        self.client.credentials()
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)