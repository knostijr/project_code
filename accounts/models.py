"""
User models for authentication and profile management.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Attributes:
        type (str): User type - 'customer' or 'business'.
        location (str): User's geographical location.
        tel (str): User's telephone number.
        description (str): User's profile description/bio.
        working_hours (int): Available working hours per week.
        created_at (datetime): Timestamp when user was created.
        updated_at (datetime): Timestamp when user was last updated.
    """

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='customer',
        help_text="Type of user account"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="User's location"
    )
    tel = models.CharField(
        max_length=20,
        blank=True,
        help_text="Telephone number"
    )
    description = models.TextField(
        blank=True,
        help_text="Profile description"
    )
    working_hours = models.IntegerField(
        default=0,
        help_text="Working hours per week"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """String representation of User."""
        return f"{self.username} ({self.get_type_display()})"