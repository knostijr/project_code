"""
Serializers for offer management.
"""

from rest_framework import serializers
from offers.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a single OfferDetail (package tier).
    """

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer including nested OfferDetail list.

    On create/update, nested details are handled manually.
    """

    details = OfferDetailSerializer(many=True, required=False)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'details',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create an offer with nested detail packages.

        Args:
            validated_data (dict): Validated data including nested details.

        Returns:
            Offer: Newly created offer with all details.
        """
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer

    def update(self, instance, validated_data):
        """
        Update an offer and replace its nested details.

        Args:
            instance (Offer): Existing offer instance.
            validated_data (dict): Validated update data.

        Returns:
            Offer: Updated offer instance.
        """
        details_data = validated_data.pop('details', None)

        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if details_data is not None:
            instance.details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)

        return instance