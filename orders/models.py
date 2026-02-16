"""
Models for order management.
"""

from django.db import models
from django.conf import settings
from offers.models import Offer, OfferDetail


class Order(models.Model):
    """
    Represents a customer placing an order on a specific offer package.

    The business_user is automatically set from the offer owner.

    Attributes:
        customer_user (ForeignKey): The customer placing the order.
        business_user (ForeignKey): The freelancer who owns the offer.
        offer (ForeignKey): The parent offer.
        offer_detail (ForeignKey): The specific package chosen.
        title (str): Order title.
        status (str): Current order status.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        help_text="Customer who placed this order"
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_orders',
        help_text="Business user who owns the offer"
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The offer being ordered"
    )
    offer_detail = models.ForeignKey(
        OfferDetail,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The specific package selected"
    )
    title = models.CharField(
        max_length=200,
        help_text="Order title"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current order status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        """String representation of Order."""
        return f"Order #{self.id}: {self.title} - {self.get_status_display()}"