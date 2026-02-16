"""
URL configuration for offers app.
"""

from django.urls import path
from . import views

app_name = 'offers'

urlpatterns = [
    path('offers/', views.OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', views.OfferDetailItemView.as_view(), name='offerdetail-item'),
]