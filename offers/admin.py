"""
Admin configuration for offers app.
"""

from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """
    Inline display of OfferDetail inside Offer admin page.
    """
    model = OfferDetail
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """
    Admin configuration for Offer model.
    """
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """
    Admin configuration for OfferDetail model.
    """
    list_display = ['offer', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type']
    search_fields = ['offer__title']