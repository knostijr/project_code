"""
Tests for the custom User model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserModelTest(TestCase):
    """
    Tests for User model fields, defaults, and behavior.
    """

    def setUp(self):
        """
        Create a base test user before each test.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!"
        )

    def test_user_creation(self):
        """
        Test that a user is created with correct credentials.
        """
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("TestPass123!"))

    def test_user_default_type(self):
        """
        Test that the default user type is 'customer'.
        """
        self.assertEqual(self.user.type, "customer")

    def test_user_type_business(self):
        """
        Test creating a user with type 'business'.
        """
        business_user = User.objects.create_user(
            username="businessuser",
            email="business@example.com",
            password="TestPass123!",
            type="business"
        )
        self.assertEqual(business_user.type, "business")

    def test_user_created_at_auto_set(self):
        """
        Test that created_at is automatically set on creation.
        """
        before = timezone.now()
        user = User.objects.create_user(
            username="timeuser",
            email="time@example.com",
            password="TestPass123!"
        )
        after = timezone.now()

        self.assertGreaterEqual(user.created_at, before)
        self.assertLessEqual(user.created_at, after)

    def test_user_str_representation(self):
        """
        Test the __str__ output of User.
        """
        self.assertEqual(str(self.user), "testuser (Customer)")

    def test_user_optional_fields_blank(self):
        """
        Test that optional fields default to blank/zero.
        """
        self.assertEqual(self.user.location, "")
        self.assertEqual(self.user.tel, "")
        self.assertEqual(self.user.description, "")
        self.assertEqual(self.user.working_hours, 0)

    def test_user_optional_fields_filled(self):
        """
        Test that optional fields can be saved and retrieved.
        """
        self.user.location = "Berlin"
        self.user.tel = "123456789"
        self.user.description = "I am a developer"
        self.user.working_hours = 40
        self.user.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.location, "Berlin")
        self.assertEqual(self.user.tel, "123456789")
        self.assertEqual(self.user.description, "I am a developer")
        self.assertEqual(self.user.working_hours, 40)

    def test_multiple_users(self):
        """
        Test that multiple users can exist simultaneously.
        """
        User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="TestPass123!"
        )
        self.assertEqual(User.objects.count(), 2)