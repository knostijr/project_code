"""
Tests for offer API endpoints.
GET/POST  /api/offers/
GET/PATCH/DELETE /api/offers/<id>/
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from offers.models import Offer, OfferDetail

User = get_user_model()


class OfferListCreateAPITest(APITestCase):
    """
    Tests for GET /api/offers/ and POST /api/offers/
    """

    def setUp(self):
        """
        Create business and customer users with tokens.
        """
        self.client = APIClient()

        self.business_user = User.objects.create_user(
            username='bizuser',
            email='biz@example.com',
            password='TestPass123!',
            type='business'
        )
        self.biz_token = Token.objects.create(user=self.business_user)

        self.customer_user = User.objects.create_user(
            username='custuser',
            email='cust@example.com',
            password='TestPass123!',
            type='customer'
        )
        self.cust_token = Token.objects.create(user=self.customer_user)

    def test_list_offers_public(self):
        """
        Test that offers can be listed without authentication.
        """
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_offers_empty(self):
        """
        Test listing offers returns empty list when no offers exist.
        """
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_offer_success(self):
        """
        Test creating an offer with nested details returns 201.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.biz_token.key)

        data = {
            'title': 'Website Design',
            'description': 'Full website design service',
            'details': [
                {
                    'title': 'Basic Website',
                    'revisions': 2,
                    'delivery_time_in_days': 7,
                    'price': '150.00',
                    'features': ['Responsive', 'SEO'],
                    'offer_type': 'basic'
                }
            ]
        }
        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Website Design')
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 1)

    def test_create_offer_with_all_tiers(self):
        """
        Test creating an offer with basic, standard, and premium packages.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.biz_token.key)

        data = {
            'title': 'Full Service',
            'description': 'All packages included',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 1,
                    'delivery_time_in_days': 3,
                    'price': '50.00',
                    'features': ['Feature A'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard',
                    'revisions': 3,
                    'delivery_time_in_days': 5,
                    'price': '100.00',
                    'features': ['Feature A', 'Feature B'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium',
                    'revisions': 5,
                    'delivery_time_in_days': 10,
                    'price': '200.00',
                    'features': ['Feature A', 'Feature B', 'Feature C'],
                    'offer_type': 'premium'
                }
            ]
        }
        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_create_offer_unauthorized(self):
        """
        Test that creating an offer without auth returns 401.
        """
        data = {
            'title': 'Test',
            'description': 'Test'
        }
        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OfferDetailRetrieveUpdateDeleteAPITest(APITestCase):
    """
    Tests for GET/PATCH/DELETE /api/offers/<id>/
    """

    def setUp(self):
        """
        Create users, tokens, and a sample offer with a detail.
        """
        self.client = APIClient()

        self.business_user = User.objects.create_user(
            username='bizuser',
            email='biz@example.com',
            password='TestPass123!',
            type='business'
        )
        self.biz_token = Token.objects.create(user=self.business_user)

        self.customer_user = User.objects.create_user(
            username='custuser',
            email='cust@example.com',
            password='TestPass123!',
            type='customer'
        )
        self.cust_token = Token.objects.create(user=self.customer_user)

        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional logo design'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic'
        )

    def test_get_single_offer(self):
        """
        Test retrieving a single offer by ID returns correct data.
        """
        response = self.client.get(f'/api/offers/{self.offer.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Logo Design')

    def test_get_offer_not_found(self):
        """
        Test that a non-existent offer ID returns 404.
        """
        response = self.client.get('/api/offers/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_offer_owner(self):
        """
        Test that the offer owner can update the offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.biz_token.key)

        data = {'title': 'Updated Logo Design'}
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Logo Design')

    def test_update_offer_not_owner(self):
        """
        Test that a non-owner gets 403 when trying to update.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.cust_token.key)

        data = {'title': 'Hacked!'}
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_owner(self):
        """
        Test that the owner can delete their offer.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.biz_token.key)

        response = self.client.delete(f'/api/offers/{self.offer.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_not_owner(self):
        """
        Test that a non-owner gets 403 when trying to delete.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.cust_token.key)

        response = self.client.delete(f'/api/offers/{self.offer.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())