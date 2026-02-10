"""
URL configuration for accounts app - Authentication.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    
    # Profiles
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile-detail'),
    path('profiles/business/', views.ProfileBusinessView.as_view(), name='profile-business'),
    path('profiles/customer/', views.ProfileCustomerView.as_view(), name='profile-customer'),
]