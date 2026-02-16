"""
Tests for Offer and OfferDetail models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from offers.models import Offer, OfferDetail

User = get_user_model()


class OfferModelTest(TestCase):
    """
    Tests for the Offer model.
    """

    def setUp(self):
        """
        Create a business user and a sample offer.
        """
        self.user = User.objects.create_user(
            username='bizuser',
            email='biz@example.com',
            password='TestPass123!',
            type='business'
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title='Logo Design',
            description='I will design a logo'
        )

    def test_offer_creation(self):
        """
        Test that an offer is created with correct fields.
        """
        self.assertEqual(self.offer.title, 'Logo Design')
        self.assertEqual(self.offer.user, self.user)
        self.assertEqual(self.offer.description, 'I will design a logo')

    def test_offer_str_representation(self):
        """
        Test __str__ output of Offer.
        """
        self.assertEqual(str(self.offer), 'Logo Design by bizuser')

    def test_offer_created_at_auto_set(self):
        """
        Test that created_at is automatically set.
        """
        self.assertIsNotNone(self.offer.created_at)

    def test_offer_cascade_delete_on_user(self):
        """
        Test that deleting a user also deletes their offers.
        """
        offer_id = self.offer.id
        self.user.delete()
        self.assertFalse(Offer.objects.filter(id=offer_id).exists())

    def test_multiple_offers_per_user(self):
        """
        Test that a user can create multiple offers.
        """
        Offer.objects.create(
            user=self.user,
            title='Second Offer',
            description='Another service'
        )
        self.assertEqual(Offer.objects.filter(user=self.user).count(), 2)

    def test_offer_image_optional(self):
        """
        Test that image field can be null/blank.
        """
        #self.assertIsNone(self.offer.image)
        self.assertFalse(self.offer.image)


class OfferDetailModelTest(TestCase):
    """
    Tests for the OfferDetail model (packages).
    """

    def setUp(self):
        """
        Create user, offer, and a basic detail package.
        """
        self.user = User.objects.create_user(
            username='bizuser',
            email='biz@example.com',
            password='TestPass123!',
            type='business'
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title='Logo Design',
            description='I will design a logo'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='basic'
        )

    def test_detail_creation(self):
        """
        Test that an OfferDetail is created with correct fields.
        """
        self.assertEqual(self.detail.title, 'Basic Design')
        self.assertEqual(self.detail.price, 100.00)
        self.assertEqual(self.detail.offer_type, 'basic')
        self.assertEqual(self.detail.revisions, 2)
        self.assertEqual(self.detail.delivery_time_in_days, 5)

    def test_detail_str_representation(self):
        """
        Test __str__ output of OfferDetail.
        """
        self.assertEqual(str(self.detail), 'Logo Design - Basic')

    def test_detail_features_json(self):
        """
        Test that features are stored and retrieved as JSON list.
        """
        self.detail.refresh_from_db()
        self.assertEqual(self.detail.features, ['Logo Design', 'Visitenkarte'])

    def test_unique_offer_type_per_offer(self):
        """
        Test that duplicate offer_type per offer raises IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            OfferDetail.objects.create(
                offer=self.offer,
                title='Another Basic',
                revisions=1,
                delivery_time_in_days=3,
                price=50.00,
                features=[],
                offer_type='basic'  # Bereits vorhanden!
            )

    def test_three_tiers_per_offer(self):
        """
        Test that an offer can have basic, standard, and premium tiers.
        """
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5,
            delivery_time_in_days=7,
            price=200.00,
            features=['Logo', 'Visitenkarte', 'Briefpapier'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10,
            delivery_time_in_days=10,
            price=500.00,
            features=['Logo', 'Visitenkarte', 'Briefpapier', 'Flyer'],
            offer_type='premium'
        )
        self.assertEqual(self.offer.details.count(), 3)

    def test_cascade_delete_on_offer_delete(self):
        """
        Test that deleting an offer also deletes its details.
        """
        detail_id = self.detail.id
        self.offer.delete()
        self.assertFalse(OfferDetail.objects.filter(id=detail_id).exists())