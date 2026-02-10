"""
Models for freelancer offers.
"""

from django.db import models
from django.conf import settings


class Offer(models.Model):
    """
    Model representing a freelancer's service offer.

    Each offer belongs to a business user and can contain
    multiple detail packages (Basic, Standard, Premium).

    Attributes:
        user (ForeignKey): The business user who created this offer.
        title (str): Title of the offer.
        image (ImageField): Main image for the offer.
        description (str): Detailed description.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        help_text="Business user who created this offer"
    )
    title = models.CharField(
        max_length=200,
        help_text="Title of the offer"
    )
    image = models.ImageField(
        upload_to='offers/',
        blank=True,
        null=True,
        help_text="Main image for the offer"
    )
    description = models.TextField(
        help_text="Detailed description of the service"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def __str__(self):
        """String representation of Offer."""
        return f"{self.title} by {self.user.username}"


class OfferDetail(models.Model):
    """
    Model representing a package tier within an offer.

    Each offer can have up to 3 tiers: basic, standard, premium.
    Each tier has its own price, delivery time, features, and revisions.

    Attributes:
        offer (ForeignKey): The parent offer.
        title (str): Package name (e.g. 'Basic Design').
        revisions (int): Number of allowed revisions.
        delivery_time_in_days (int): Delivery time in days.
        price (Decimal): Price of this package.
        features (list): JSON list of included features.
        offer_type (str): Package tier - basic, standard, or premium.
    """

    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
        help_text="Parent offer"
    )
    title = models.CharField(
        max_length=100,
        help_text="Package name"
    )
    revisions = models.IntegerField(
        default=0,
        help_text="Number of revisions included"
    )
    delivery_time_in_days = models.IntegerField(
        help_text="Delivery time in days"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Package price"
    )
    features = models.JSONField(
        default=list,
        help_text="List of features included"
    )
    offer_type = models.CharField(
        max_length=20,
        choices=OFFER_TYPE_CHOICES,
        help_text="Package tier type"
    )

    class Meta:
        ordering = ['offer', 'offer_type']
        verbose_name = 'Offer Detail'
        verbose_name_plural = 'Offer Details'
        unique_together = ['offer', 'offer_type']

    def __str__(self):
        """String representation of OfferDetail."""
        return f"{self.offer.title} - {self.get_offer_type_display()}"