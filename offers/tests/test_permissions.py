"""
Permission tests for offers app.
Ensures only offer owners can edit/delete, and public endpoints are accessible.
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from offers.models import Offer, OfferDetail

User = get_user_model()


class OffersPermissionTest(APITestCase):
    """
    Tests that offers list/detail is public,
    but create/update/delete require correct ownership.
    """

    def setUp(self):
        """
        Create two business users and one offer owned by user_a.
        """
        self.client = APIClient()

        self.user_a = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='TestPass123!',
            type='business'
        )
        self.token_a = Token.objects.create(user=self.user_a)

        self.user_b = User.objects.create_user(
            username='stranger',
            email='stranger@example.com',
            password='TestPass123!',
            type='business'
        )
        self.token_b = Token.objects.create(user=self.user_b)

        self.offer = Offer.objects.create(
            user=self.user_a,
            title='Owner Offer',
            description='Only owner can edit this'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=1,
            delivery_time_in_days=3,
            price=50.00,
            features=['Feature A'],
            offer_type='basic'
        )

    def test_list_offers_no_auth(self):
        """
        GET /api/offers/ is public.
        """
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offer_no_auth(self):
        """
        GET /api/offers/<id>/ is public.
        """
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_offer_no_auth_forbidden(self):
        """
        POST /api/offers/ without token returns 401.
        """
        data = {'title': 'Hack', 'description': 'Test'}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_offer_owner_allowed(self):
        """
        Owner can PATCH their own offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_a.key)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'Updated by Owner'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_offer_stranger_forbidden(self):
        """
        Non-owner gets 403 on PATCH.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'Hacked!'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_owner_allowed(self):
        """
        Owner can DELETE their own offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_a.key)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_offer_stranger_forbidden(self):
        """
        Non-owner gets 403 on DELETE.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_b.key)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())