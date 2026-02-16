"""
Views for offer management.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from offers.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer


class OfferListCreateView(generics.ListCreateAPIView):
    """
    List all offers or create a new one.

    GET  /api/offers/  - public list
    POST /api/offers/  - requires auth, only business users
    """

    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Automatically assign current user as the offer owner.

        Args:
            serializer: Validated serializer ready to save.
        """
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single offer.

    GET    /api/offers/<id>/  - public
    PATCH  /api/offers/<id>/  - only owner
    DELETE /api/offers/<id>/  - only owner
    """

    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        """
        Only the offer owner can update.

        Returns:
            Response: Updated data or 403 Forbidden.
        """
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'You do not have permission to edit this offer.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Only the offer owner can delete.

        Returns:
            Response: 204 No Content or 403 Forbidden.
        """
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'You do not have permission to delete this offer.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class OfferDetailItemView(generics.RetrieveAPIView):
    """
    Retrieve a single OfferDetail by its ID.

    GET /api/offerdetails/<id>/
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]